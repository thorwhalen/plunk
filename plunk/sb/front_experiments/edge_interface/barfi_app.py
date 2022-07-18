# Usage: streamlit run barfi_app.py


from barfi import st_barfi, Block

feed = Block(name="Feed")
feed.add_output()

result = Block(name="Result")
result.add_output()

st_barfi(base_blocks=[feed, result])
