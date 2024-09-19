import streamlit as st
import google.generativeai as genai
from streamlit_lottie import st_lottie
import requests
import json
import plotly.graph_objects as go
from streamlit_ace import st_ace
from streamlit_option_menu import option_menu
from streamlit_particles import particles
import extra_streamlit_components as stx

# Configure the Gemini API
genai.configure(api_key='YOUR_API_KEY_HERE')

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
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    )])

    fig.update_layout(
        title_text='Code Analysis Summary',
        xaxis_title='Metrics',
        yaxis_title='Count',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

def main():
    st.set_page_config(page_title="Code Analyzer Pro", page_icon="🚀", layout="wide")

    # Custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-radius: 10px;
    }
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-radius: 10px;
    }
    .css-1y4p8pa {
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .css-1y4p8pa .stMarkdown a {
        color: #4CAF50;
    }
    .stPlotlyChart {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Particles background
    particles(
        options={
            "particles": {
                "number": {"value": 50},
                "color": {"value": "#ffffff"},
                "shape": {"type": "circle"},
                "opacity": {"value": 0.5, "random": True},
                "size": {"value": 3, "random": True},
                "move": {"enable": True, "speed": 1},
            },
            "interactivity": {
                "events": {"onhover": {"enable": True, "mode": "repulse"}},
            },
        },
    )

    # Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("🚀 Code Analyzer Pro")
        st.markdown("#### Elevate your Python code with AI-powered analysis")
    with col2:
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json"
        lottie_json = load_lottie_url(lottie_url)
        st_lottie(lottie_json, height=200, key="coding")

    st.markdown("---")

    # Main navigation
    selected = option_menu(
        menu_title=None,
        options=["Code Input", "Analysis Results", "Help"],
        icons=["code-slash", "graph-up", "question-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if selected == "Code Input":
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

        if st.button("🔬 Analyze Code", type="primary"):
            if code and test_case:
                with st.spinner("🧠 AI is working its magic..."):
                    result = dry_run_code(code, test_case)
                st.session_state.result = result
                st.session_state.analysis_done = True
                st.success("🎉 Analysis complete! Switch to the Analysis Results tab to view insights.")
            else:
                st.error("⚠️ Oops! We need both the code and a test case to perform the analysis.")

    elif selected == "Analysis Results":
        if 'analysis_done' in st.session_state and st.session_state.analysis_done:
            result = st.session_state.result
            try:
                summary_start = result.rfind('{')
                summary_end = result.rfind('}') + 1
                summary_json = result[summary_start:summary_end]
                summary_data = json.loads(summary_json)

                col_chart, col_details = st.columns([1, 2])
                with col_chart:
                    fig = create_summary_chart(summary_data)
                    st.plotly_chart(fig, use_container_width=True)

                with col_details:
                    st.markdown("### 🔍 Dry Run Insights")
                    tabs = stx.tab_bar(data=[
                        stx.TabBarItemData(id=1, title="Analysis", description="Detailed analysis"),
                        stx.TabBarItemData(id=2, title="Errors", description="Found issues"),
                        stx.TabBarItemData(id=3, title="Optimizations", description="Suggestions"),
                    ])
                    
                    if tabs == '1':
                        st.markdown(result[:summary_start])
                    elif tabs == '2':
                        st.markdown("### Errors and Issues")
                        st.markdown("Details about errors found in the code...")
                    elif tabs == '3':
                        st.markdown("### Optimization Suggestions")
                        st.markdown("Suggestions for improving the code...")

            except json.JSONDecodeError as e:
                st.error(f"Error parsing JSON: {str(e)}")
                st.write("Full AI response:", result)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Full AI response:", result)
        else:
            st.info("No analysis results yet. Please go to the Code Input tab and analyze your code first.")

    elif selected == "Help":
        st.markdown("""
        ### How to use Code Analyzer Pro
        1. **Input Your Code**: In the 'Code Input' tab, paste your Python code into the editor.
        2. **Provide a Test Case**: Describe a scenario or input for your code.
        3. **Run Analysis**: Click the 'Analyze Code' button to start the AI-powered analysis.
        4. **View Results**: Switch to the 'Analysis Results' tab to see detailed insights.
        5. **Interpret the Chart**: The bar chart shows a summary of the analysis metrics.
        6. **Read Detailed Insights**: Explore the tabs for in-depth analysis, errors, and optimization tips.

        ### Tips for Best Results
        - Provide clear and concise test cases for more accurate analysis.
        - Review all sections of the analysis for a comprehensive understanding.
        - Use the optimization suggestions to improve your code quality.

        For more information, visit our [documentation](#) or [contact support](#).
        """)

    # Sidebar
    with st.sidebar:
        st.title("📚 Code Analyzer Pro")
        st.markdown("---")
        st.subheader("About")
        st.info(
            "Code Analyzer Pro uses cutting-edge AI to perform an in-depth dry run analysis of your Python code. "
            "Get insights into execution flow, variable changes, and potential optimizations."
        )
        st.markdown("---")
        st.subheader("Latest Updates")
        st.success("✨ New feature: Interactive particle background\n🔧 Improved error detection\n📊 Enhanced visualization of results")
        
    if 'analysis_done' in st.session_state and st.session_state.analysis_done:
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="📥 Download Analysis Report",
            data=st.session_state.result,
            file_name="code_analysis_report.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
