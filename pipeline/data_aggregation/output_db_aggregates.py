import luigi

from pipeline.common.read import get_table_columns, generate_analytics_path
from pipeline.common.tasks import OutputDatabaseTask
from pipeline.database.aggregates_insert import InsertCoinAggregates
from pipeline.database.trends_insert import InsertDailyTrends

_config = luigi.configuration.get_config()
_population_aggregates_table = _config.get('database', 'population-aggregates-table')
_hourly_trends_table = _config.get('database', 'hourly-trends-table')
_daily_trends_table = _config.get('database', 'daily-trends-table')
_coin_aggregates_table = _config.get('database', 'coin-aggregates-table')
_group = 'db-aggregations'


class OutputDailyTrends(OutputDatabaseTask):
    date = luigi.DateParameter()

    def requires(self):
        return InsertDailyTrends(**self.param_kwargs)

    @property
    def output_path(self):
        return (
            generate_analytics_path(group=_group,
                                    name='daily-trends',
                                    date=self.date)
        )

    table = _daily_trends_table
    columns = get_table_columns(_daily_trends_table)


class OutputCoinAggregations(OutputDatabaseTask):
    date_hour = luigi.DateHourParameter()

    def requires(self):
        return InsertCoinAggregates(**self.param_kwargs)

    @property
    def output_path(self):
        return (
            generate_analytics_path(group=_group,
                                    name='coin-aggregations',
                                    date=self.date_hour.date(),
                                    hour=self.date_hour.hour)
        )

    table = _coin_aggregates_table
    columns = get_table_columns(_coin_aggregates_table)


class DailyDbAggregatesOutput(luigi.WrapperTask):
    date = luigi.DateParameter()

    def requires(self):
        # yield OutputHourlyTrends(**self.param_kwargs)
        yield OutputDailyTrends(**self.param_kwargs)


class HourlyDbAggregatesOutput(luigi.WrapperTask):
    date_hour = luigi.DateHourParameter()

    def requires(self):
        yield OutputCoinAggregations(**self.param_kwargs)
