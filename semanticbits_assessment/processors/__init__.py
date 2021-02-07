from semanticbits_assessment.db import session_context, db_create_engine
from semanticbits_models import Health
from enum import Enum
import pandas as pd
import datetime
import logging


class Constants(Enum):
    NE_STATES = ['CT', 'MA', 'ME', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT', 'DE', 'MD', 'DC']


class HealthProcessor:
    def __init__(self, data_file):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f'{__name__} entered')
        self.df = pd.read_csv(data_file)

    def get_subset(self) -> pd.DataFrame:
        """
        returns a subset of rows from dataframe
        based off of states defined as NE
        RETURNS
        -------
        df_sub: pd.DataFrame
            pandas dataframe
        """
        df = self.df
        self.logger.info('Getting subset of data frame')
        df_sub = df.loc[df.State.str.upper().isin(Constants.NE_STATES.value)]
        return df_sub

    def float_to_int(self, df):
        """
        change float values to integers
        """
        float_cols = ['State code', 'County code', 'Data Release Year', 'fipscode']
        for col in float_cols:
            self.logger.info(f'Transforming {col} into integer values')
            df.loc[:, col].fillna(0, inplace=True)
            df[col] = df[col].astype(int)
        return df

    def create_health(self, record) -> Health:
        """
        create the health table
        """

        info = {
            'state': record.State,
            'county': record.County,
            'state_code': record['State code'],
            'county_code': record['County code'],
            'year_span': record['Year span'],
            'measure_name': record['Measure name'],
            'measure_id': record['Measure id'],
            'numerator': record['Numerator'],
            'denominator': record['Denominator'],
            'raw_value': record['Raw value'],
            'confidence_interval_lower_bound': record['Confidence Interval Lower Bound'],
            'confidence_interval_upper_bound': record['Confidence Interval Upper Bound'],
            'data_release_year': record['Data Release Year'],
            'fipscode': record['fipscode'],
            'dt_updated': datetime.datetime.now()
        }
        return Health(**info)

    def parse_records(self, df) -> list:
        """
        parse each row from the dataframe,
        turn into a Health data object,
        and append that object ot a list
        """
        health_rows = []
        for idx, row in df.iterrows():
            health_record = self.create_health(row)
            health_rows.append(health_record)
        return health_rows

    def run(self):
        """
        get df subset, transform necessary values
        from float to int, and add record to db
        """
        df_subset = self.get_subset()
        df_transformed = self.float_to_int(df_subset)
        health_rows = self.parse_records(df_transformed)
        with session_context(db_create_engine()) as db_session:
            self.logger.info('Adding record to database.. this may take a few minutes')
            db_session.add_all(health_rows)
        self.logger.info('Health table populated successfully!')
        return







