from longevity_test import LongevityTest
from test_lib.compaction import CompactionStrategy
from test_lib.scylla_bench_tools import create_scylla_bench_table_query


class LargePartitionLongevityTest(LongevityTest):

    def test_large_partition_longevity(self):
        compaction_strategy = self.params.get('compaction_strategy')
        self.pre_create_large_partitions_schema(compaction_strategy=compaction_strategy)
        self.test_custom_time()

    def pre_create_large_partitions_schema(self, compaction_strategy=CompactionStrategy.SIZE_TIERED.value):
        node = self.db_cluster.nodes[0]
        table_setup_seed = self.params.get('cql_schema_seed')
        create_table_query = create_scylla_bench_table_query(compaction_strategy=compaction_strategy,
                                                             seed=table_setup_seed)
        with self.db_cluster.cql_connection_patient(node) as session:
            # pylint: disable=no-member
            session.execute("""
                    CREATE KEYSPACE IF NOT EXISTS scylla_bench WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3}
            """)
            session.execute(create_table_query)
