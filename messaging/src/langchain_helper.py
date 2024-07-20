import os
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from .database import Database
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,FewShotChatMessagePromptTemplate,PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
import pandas as pd
from langchain.memory import ChatMessageHistory
import requests
from langchain.chains.openai_tools import create_extraction_chain_pydantic
import os
from dotenv import load_dotenv

class Table(BaseModel):
    """Table in SQL database."""

    name: str = Field(description="Name of table in SQL database.")

class LangchainHelper:

    def __init__(self) -> None:
        load_dotenv()

    def process_propt(self, request):

        prompt = request.POST.get('prompt')

        db = Database().get_db(request)

        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        few_shot_prompts = self.create_few_shot_examples()
        generate_query = create_sql_query_chain(self.llm, db, few_shot_prompts) # Generate sql query

        execute_query = QuerySQLDataBaseTool(db=db)

        # chain = generate_query | execute_query
        # self.response = chain.invoke({'question': prompt})

        rephrase_answer = self.rephrase_answer()

        # chain = (
        #     RunnablePassthrough.assign(query=generate_query).assign(
        #         result=itemgetter("query") | execute_query
        #     )
        #     | rephrase_answer
        # )

        select_table = self.get_relative_potential_database()

        chain = (
            RunnablePassthrough.assign(table_names_to_use=select_table) |
            RunnablePassthrough.assign(query=generate_query).assign(
                result=itemgetter("query") | execute_query
            )
            | rephrase_answer
        )

        response = chain.invoke({'question': prompt})

        return {
            "response": response,
        }

    def rephrase_answer(self):
        answer_prompt = PromptTemplate.from_template(
            """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
        )

        rephrase_answer = answer_prompt | self.llm | StrOutputParser()

        return rephrase_answer

    def create_few_shot_examples(self):

        vectorstore = Chroma()
        vectorstore.delete_collection()
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            examples,
            OpenAIEmbeddings(),
            vectorstore,
            k=2,
            input_keys=["input"],
        )
        example_selector.select_examples({"input": "how many employees we have?"})

        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}\nSQLQuery:"),
                ("ai", "{query}"),
            ]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            example_selector=example_selector,
            input_variables=["input","top_k"],
        )
        # print(few_shot_prompt.format(input="How many products are there?"))

        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a MySQL expert. Given an input question, create a syntactically correct MySQL query to run. Unless otherwise specificed.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries."),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )

        return final_prompt

    def get_table_details(self):
        # Read the CSV file into a DataFrame
        table_description = pd.read_csv("/Users/harsh.ughreja/Documents/codefest/fusionworks/static/database_table_descriptions.csv")
        table_docs = []

        # Iterate over the DataFrame rows to create Document objects
        table_details = ""
        for index, row in table_description.iterrows():
            table_details = table_details + "Table Name:" + row['Table'] + "\n" + "Table Description:" + row['Description'] + "\n\n"

        return table_details

    def get_relative_potential_database(self):
        table_details = self.get_table_details()

        print(table_details)

        table_details_prompt = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
        The tables are:

        {table_details}

        Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""

        table_chain = create_extraction_chain_pydantic(Table, self.llm, system_message=table_details_prompt)

        select_table = {"input": itemgetter("question")} | create_extraction_chain_pydantic(Table, self.llm, system_message=table_details_prompt) | self.get_tables

        return select_table

    def get_tables(self, tables: List[Table]) -> List[str]:
        tables  = [table.name for table in tables]

        return tables

examples = [
     {
         "input": "List all customers in France with a credit limit over 20,000.",
         "query": "SELECT * FROM customers WHERE country = 'France' AND creditLimit > 20000;"
     },
     {
         "input": "Get the highest payment amount made by any customer.",
         "query": "SELECT MAX(amount) FROM payments;"
     },
]
