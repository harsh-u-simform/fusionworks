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

class LangchainHelper:

    def __init__(self) -> None:
        os.environ["GOOGLE_API_KEY"] = 'AIzaSyDKqBlqQwWW7DglNoXENi1VnQlW6vWT8Es'
        os.environ['OPENAI_API_KEY'] = 'sk-proj-1oj10nL0ENsfYozBIonvT3BlbkFJsYl9511dnkP7mZueTeVP'
        os.environ['LANGCHAIN_API_KEY'] = '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'
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'

    def process_propt(self, request):

        prompt = request.POST.get('prompt')

        print(prompt)

        db = Database().get_db(request)

        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        few_shot_prompts = self.create_few_shot_examples()
        generate_query = create_sql_query_chain(self.llm, db, few_shot_prompts) # Generate sql query

        execute_query = QuerySQLDataBaseTool(db=db)

        # chain = generate_query | execute_query
        # self.response = chain.invoke({'question': prompt})

        rephrase_answer = self.rephrase_answer()

        chain = (
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
