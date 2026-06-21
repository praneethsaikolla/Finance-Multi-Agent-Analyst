import sys
import os

# Add the parent directory to the path so we can import fin_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fin_agent.tools.stock_tool import stock_tool

print("Testing stock_tool('NVDA'):")
result = stock_tool.func("NVDA")
print(result)
