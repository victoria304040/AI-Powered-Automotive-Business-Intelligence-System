@tool
def analyze_dataframe(query: str) -> str:
    """使用 Pandas Agent 分析當前的資料框架，根據使用者的自然語言查詢執行操作"""
    if 'current_df' not in dataframes:
        return "尚未載入任何資料集，請先使用 read_excel_file 載入資料。"

    try:
        df = dataframes['current_df']
        
        # 執行資料清理（確保資料型態正確）
        if "日期" in df.columns:
            df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
        
        if "實績種類" in df.columns:
            df["實績種類"] = df["實績種類"].astype(str).str.strip()
        
        # 更新 dataframes
        dataframes['current_df'] = df

        # 使用 LangChain Pandas Agent 進行分析（和 solution1.py 完全一致）
        from langchain_experimental.agents import create_pandas_dataframe_agent
        from langchain_openai import ChatOpenAI
        from langchain.agents.agent_types import AgentType

        custom_llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-2024-11-20"
        )

        df_agent = create_pandas_dataframe_agent(
            custom_llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True
        )

        # 執行查詢
        result = df_agent.run(query)
        return result
        
    except Exception as e:
        return f"分析時發生錯誤: {str(e)}\n\n錯誤詳情: {type(e).__name__}"