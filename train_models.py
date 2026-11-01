from src.synthetic_data import generate
from src.models import train_compare
from pathlib import Path
if __name__=='__main__':
 Path('data').mkdir(exist_ok=True); df=generate(); df.to_csv('data/food_service_research_dataset.csv',index=False)
 print('Synthetic history created:',df.shape)
 train_compare()
