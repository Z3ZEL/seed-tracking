from interfaces.numerical_computing.data_cleaner import DataCleaner
class Computer(DataCleaner):
    def __init__(self, **kwargs) -> None:
        self.range = kwargs["range"] if "range" in kwargs else 10
        super().__init__(**kwargs)
    
    def compute(self, m_img_coords, s_img_coords) -> tuple[list, list]:
        '''
        Do nothing on the data cleaning, use for report and comparison
        '''

        return m_img_coords, s_img_coords
    

        