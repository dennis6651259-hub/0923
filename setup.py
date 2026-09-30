from setuptools import setup, find_packages

setup(
    name="taiwan-weather-dashboard",
    version="1.0.0",
    description="Taiwan Weather Forecast AI & Data Visualization Dashboard",
    author="dennis6651259-hub",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.30.0",
        "pandas>=2.0.0",
        "requests>=2.28.0",
        "folium>=0.14.0",
        "streamlit-folium>=0.15.0",
        "plotly>=5.15.0",
        "urllib3>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "weather-crawler=crawler:run_daily_crawler",
        ],
    },
    python_requires=">=3.8",
)
