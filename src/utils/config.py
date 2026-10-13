"""
This file handles the configuration settings for the project.
From the extract, transform and load stage to the viz.
Config also handles the API config, database, email, dashboard,
report and automation configuration.
"""

import os 
from dotenv import load_dotenv


class Config:
    """
    Class configuration that manages all the configuration settings
    for all phases of the lifecycel
    """

    def __init__(self) -> None:
        pass

    def get_database_path(self) -> str:
        pass

    def is_email_configured(self) -> bool:
            pass

    def string_representation_config(self) -> str:
            pass

    def __str__(self) -> str:
            pass


