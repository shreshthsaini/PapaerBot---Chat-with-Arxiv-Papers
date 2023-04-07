import arxiv
import PyPDF2
import io
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from h2o_wave import main, app, Q, ui, data

MAX_MESSAGES = 500  # Maximum number of messages to store in the chat window
index = None  # Initialize the global index variable

# Function to convert PDF to text
def pdf_to_txt(file_path):
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ''

        # Extract text from each page of the PDF
        for page in pdf_reader.pages:
            text += page.extract_text()

    return text

# Function to prepare the index for querying
def prepare_index(txt_file_path):
    global index
    loader = TextLoader(txt_file_path)
    index = VectorstoreIndexCreator().from_loaders([loader])

# Main app function that handles the UI and logic
@app('/demo')
async def serve(q: Q):
    global index

    # Initialize the UI if it hasn't been initialized yet
    if not q.client.initialized:
        # Set up the UI theme
        q.page['meta'] = ui.meta_card(box='', themes=[
                                                        ui.theme(
                                                        name='nature',
                                                        primary='#13ebe7',
                                                        text='#e8e1e1',
                                                        card='#12123b',
                                                        page='#070b1a',
                                                        ),
            ],
            theme='nature'
        )

        # Set up the chat title
        q.page['chat_title'] = ui.form_card(
        box='3 1 9 1',
        items=[
        ui.text('<h1 style="text-align: center; color: #50fa7b;">Paper Bot: Chat with Your Papers</h1>'),
        ]
        )

        # Set up the chat window
        cyclic_buffer = data(fields='msg fromUser', size=-MAX_MESSAGES)
        #q.page['chat'] = ui.chatbot_card(box='3 2 9 8', data=cyclic_buffer, name='chat')

        # Set up the input form for Arxiv ID and query
        q.page['input'] = ui.form_card(box='3 8 9 3', items=[
            ui.textbox(name='arxiv_id', label='Arxiv ID', placeholder='Enter Arxiv ID (e.g. 00000.1111)', disabled=q.client.arxiv_id_set),
            ui.textbox(name='query', label='Query', placeholder='Enter your query'),
            ui.buttons(items=[ui.button(name='submit', label='Submit', primary=True)]),
        ])

        # Initialize client variables
        q.client.arxiv_id = None
        q.client.arxiv_id_set = False
        q.client.initialized = True
        await q.page.save()

    # Handle the submit button click
    if q.args.submit:
        user_query = q.args.query

        # If Arxiv ID is not set, set it
        if not q.client.arxiv_id:
            q.client.arxiv_id = q.args.arxiv_id

            # Check if Arxiv ID is valid
            if not q.client.arxiv_id:
                q.page['chat'].data[-1] = ["Not a Valid Arxiv ID.", False]
                await q.page.save()
                return

            # Download the paper and convert it to text
            search = arxiv.Search(id_list=[q.client.arxiv_id])
            paper = next(search.results())
            paper.download_pdf(filename="temp-paper.pdf")

            pdf_file_path = 'temp-paper.pdf'
            txt_file_path = 'converted-paper.txt'

            text = pdf_to_txt(pdf_file_path)

            # Save the text to a file
            with io.open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(text)

            # Prepare the index for querying
            prepare_index(txt_file_path)

        # Query the index if it exists
        if index:
            response = index.query(user_query)
            # Append user message
            q.page['chat'].data[-1] = [f"User: {user_query}", True]
            # Append bot response
            q.page['chat'].data[-1] = [f"Bot: {response}", False]

            q.client.arxiv_id_set = True

        await q.page.save()

# Main entry point
if __name__ == '__main__':
    main()