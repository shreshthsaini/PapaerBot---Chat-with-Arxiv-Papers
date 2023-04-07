Simple application based on langchain to interact with arxiv papers. [https://python.langchain.com]
Also, for chat interaction and UI - H2O.ai

                pip install -r requirements.txt

If using conda env (for mac-book pro): 

                pip install https://github.com/h2oai/wave/releases/download/nightly/h2o_wave-nightly-py3-none-macosx_10_9_x86_64.whl

Install wave server and run it separately in env (for conda/mac): 
    
        https://h2o-wave.s3.amazonaws.com/releases/wave-0.25.2-darwin-arm64.tar.gz


For OpenAI api key: 
        
            export OPENAI_API_KEY="YOUR_KEY_GOES_HERE"

Run: 
    
            wave run arxiv_chat_app 

Openapp on localhost:10101/demo 

Use: 

1. give paper_id/number :
2. Q/A



NOTE: 
1. Use conda env with python version 3.10.10
2. Make sure you have C++ 11 or higher compiler installed [for $hnswlib$ package]
-- to reinstall or update xcode command line tools: 
        xcode-select --install
