import unittest
import repository
class RepositoryTest(unittest.TestCase):
    def test_constructor(self):
        try:
            instance = repository.JsonFileRepository()
            self.assertTrue(False)
        except NotImplementedError:
            self.assertTrue(True)

    def test_get_instance(self):
        instance = repository.JsonFileRepository.get_instance()
        self.assertTrue(isinstance(instance, repository.JsonFileRepository))
        self.assertTrue(isinstance(instance, repository.IRepository))

        instance2 = repository.JsonFileRepository.get_instance()
        self.assertEqual(instance.__hash__, instance2.__hash__)

    def test_get_switch_record_by_switch_name_when_not_called_init(self):
        instance = repository.JsonFileRepository.get_instance()
        try:
            instance.get_switch_record_by_switch_name("test")
            self.assertTrue(False)
        except repository.UnInitializedError:
            self.assertTrue(True)

    def test_update_state_by_switch_name_when_not_called_init(self):
        instance = repository.JsonFileRepository.get_instance()
        try:
            instance.update_state_by_switch_name("test",False)
            self.assertTrue(False)
        except repository.UnInitializedError:
            self.assertTrue(True)
