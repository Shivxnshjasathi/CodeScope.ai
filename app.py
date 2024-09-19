import streamlit as st
import google.generativeai as genai
from streamlit_lottie import st_lottie
import requests
import json
import plotly.graph_objects as go
from streamlit_ace import st_ace

# Configure the Gemini API
genai.configure(api_key='AIzaSyBGwV0hwIhXw8OdeGBX8PyMbEepxLXeP9k')

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def dry_run_code(code, test_case):
    """Perform a dry run of the provided Python code with a test case."""
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Perform a dry run of the following code with the provided test case. Explain each step of execution, with the step and changes in the variables at each step.
    Include variable assignments and their values at each step. If there are any
    errors or potential issues, point them out and also give optimal solution.
    Additionally, provide a summary of the analysis in JSON format with the following structure:
    {{
        "execution_steps": <number of steps>,
        "variables_tracked": <number of variables tracked>,
        "errors_found": <number of errors found>,
        "optimization_suggestions": <number of optimization suggestions>
    }}

    Code:
    {code}

    Test Case:
    {test_case}

    Dry Run Analysis:
    """
    
    response = model.generate_content(prompt)
    return response.text

def create_summary_chart(summary_data):
    categories = list(summary_data.keys())
    values = list(summary_data.values())

    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=['#FFA07A', '#98FB98', '#87CEFA', '#DDA0DD']
    )])

    fig.update_layout(
        title_text='Code Analysis Summary',
        xaxis_title='Metrics',
        yaxis_title='Count',
        template='plotly_white'
    )

    return fig

def main():
    st.set_page_config(page_title="Code Analyzer Pro", page_icon="🚀", layout="wide")

    # Custom CSS (same as before)
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #2b5876, #4e4376);
        color: #ffffff;
    }
    /* ... (rest of the CSS remains the same) ... */
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.title("🚀 Code Analyzer Pro")
        st.markdown("#### Elevate your Python code with AI-powered analysis")

    with col2:
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json"
        lottie_json = load_lottie_url(lottie_url)
        st_lottie(lottie_json, height=200, key="coding")

    st.markdown("---")

    tabs = st.tabs(["Code Input", "Analysis Results"])

    with tabs[0]:
        col_code, col_test = st.columns(2)

        with col_code:
            st.subheader("📝 Your Masterpiece")
            code = st_ace(
                placeholder="Paste your Python code here...",
                language="python",
                theme="monokai",
                keybinding="vscode",
                min_lines=20,
                key="code_editor"
            )

        with col_test:
            st.subheader("🧪 Test Scenario")
            test_case = st.text_area("", height=400, key="test_case_input", placeholder="Describe your test case here...")

    with tabs[1]:
        if 'analysis_done' not in st.session_state:
            st.session_state.analysis_done = False

        if st.button("🔬 Analyze Code", type="primary"):
            if code and test_case:
                with st.spinner("🧠 AI is working its magic..."):
                    result = dry_run_code(code, test_case)
                
                st.success("🎉 Analysis complete!")
                
                # Extract summary data from the result
                try:
                    summary_start = result.rfind('{')
                    summary_end = result.rfind('}') + 1
                    summary_json = result[summary_start:summary_end]
                    
                    # Debug information
                    st.write("Debug: JSON content")
                    st.code(summary_json)
                    
                    summary_data = json.loads(summary_json)

                    col_chart, col_details = st.columns([1, 2])

                    with col_chart:
                        fig = create_summary_chart(summary_data)
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#ffffff'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col_details:
                        st.markdown("### 🔍 Dry Run Insights")
                        with st.expander("View Detailed Analysis", expanded=True):
                            st.markdown(result[:summary_start])  # Exclude the summary JSON from the detailed analysis

                    st.session_state.analysis_done = True
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing JSON: {str(e)}")
                    st.write("Full AI response:")
                    st.write(result)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.write("Full AI response:")
                    st.write(result)
            else:
                st.error("⚠️ Oops! We need both the code and a test case to perform the analysis.")

    # Sidebar content (same as before)
    st.sidebar.title("📚 Code Analyzer Pro")
    # ... (rest of the sidebar content remains the same) ...

    if st.session_state.analysis_done:
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="📥 Download Analysis Report",
            data=result,
            file_name="code_analysis_report.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
