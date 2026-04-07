import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.loader import run_all_loaders
if __name__=="__main__":
    run_all_loaders()
