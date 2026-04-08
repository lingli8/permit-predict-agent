from langgraph.checkpoint.memory import MemorySaver

# In-memory checkpointer for short-term (within-session) conversation memory.
# To persist across server restarts, swap MemorySaver for SqliteSaver or PostgresSaver.
memory = MemorySaver()
