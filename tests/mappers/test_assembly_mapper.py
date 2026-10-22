import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from api.consume.gen.factory.models.assembly_status import AssemblyStatus
from business.mappers.assembly_mapper import fromAssemblyToTable

ASSEMBLY_ID = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")


def build_assembly(assembly_id):
    return SimpleNamespace(
        id=assembly_id,
        created_at=datetime(2026, 10, 5, 12, 0, 0, tzinfo=timezone.utc),
        factory_type='SALE_OFFER_UPSERT',
        tags=[],
        status=AssemblyStatus.PENDING,
        failed_steps=0,
        successful_steps=0,
        total_steps=10,
        output=None
    )


class TestAssemblyMapper(unittest.TestCase):

    def test_id_is_exposed_to_qml_as_a_string(self):
        # A uuid.UUID has no QML counterpart: it would cross the boundary as an opaque
        # QVariant(PySide::PyObjectWrapper) and come back to downloadAndOpenFile as that
        # wrapper's repr instead of the assembly id (LDS-6239).
        row = fromAssemblyToTable(build_assembly(ASSEMBLY_ID))

        self.assertIsInstance(row['id'], str)
        self.assertEqual(row['id'], '3fa85f64-5717-4562-b3fc-2c963f66afa6')

    def test_missing_id_stays_none(self):
        row = fromAssemblyToTable(build_assembly(None))

        self.assertIsNone(row['id'])


if __name__ == '__main__':
    unittest.main()
