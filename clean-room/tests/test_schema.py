import json
from pathlib import Path
import shutil
import tempfile
import unittest

from public_parameters import validate_public_parameters
from schema import InputValidationError, validate_cover_file, validate_input_directory


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "inputs"


class InputSchemaTests(unittest.TestCase):
    def test_all_copied_inputs_pass_syntactic_validation(self):
        inventories, hashes = validate_input_directory(INPUTS)
        self.assertEqual(len(inventories), 38)
        self.assertEqual(len(hashes), 39)
        validate_public_parameters(INPUTS)

    def mutate_one(self, relative, mutation):
        source = INPUTS / relative
        document = json.loads(source.read_text(encoding="utf-8"))
        mutation(document)
        temporary = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        self.addCleanup(lambda: Path(temporary.name).unlink(missing_ok=True))
        json.dump(document, temporary)
        temporary.close()
        return Path(temporary.name)

    def test_unknown_field_is_rejected(self):
        path = self.mutate_one("local/0.json", lambda document: document.update({"passed": True}))
        with self.assertRaisesRegex(InputValidationError, "unknown fields"):
            validate_cover_file(path, "local/0.json")

    def test_unknown_witness_field_is_rejected(self):
        def mutate(document):
            document["witnesses"][0]["valid"] = True

        path = self.mutate_one("local/0.json", mutate)
        with self.assertRaisesRegex(InputValidationError, "unknown witness"):
            validate_cover_file(path, "local/0.json")

    def test_malformed_rational_is_rejected(self):
        def mutate(document):
            document["parameters"]["shape"]["tube"]["radius"] = "0.01"

        path = self.mutate_one("local/0.json", mutate)
        with self.assertRaises(InputValidationError):
            validate_cover_file(path, "local/0.json")

    def test_broken_witness_reference_is_rejected(self):
        def mutate(document):
            document["zooms"][0]["leaves"][0]["witness"]["index"] = len(document["witnesses"])

        path = self.mutate_one("local/0.json", mutate)
        with self.assertRaisesRegex(InputValidationError, "invalid reference"):
            validate_cover_file(path, "local/0.json")

    def test_negative_factor_exponent_is_rejected(self):
        def mutate(document):
            document["zooms"][0]["leaves"][0]["witness"]["factor"][2] = -1

        path = self.mutate_one("local/0.json", mutate)
        with self.assertRaisesRegex(InputValidationError, "nonnegative"):
            validate_cover_file(path, "local/0.json")

    def copied_inputs(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name) / "inputs"
        shutil.copytree(INPUTS, target)
        return target

    def rewrite(self, root, relative, mutation):
        path = root / relative
        document = json.loads(path.read_text(encoding="utf-8"))
        mutation(document)
        path.write_text(json.dumps(document), encoding="utf-8")

    def test_changed_root_bound_is_rejected(self):
        copied = self.copied_inputs()
        self.rewrite(
            copied,
            "local/0.json",
            lambda document: document["parameters"]["shape"]["tube"]["base"][0].__setitem__(1, "1/5"),
        )
        with self.assertRaisesRegex(InputValidationError, "Appendix B"):
            validate_public_parameters(copied)

    def test_enlarged_handover_window_is_rejected(self):
        copied = self.copied_inputs()
        self.rewrite(
            copied,
            "exotic/crossing+.json",
            lambda document: document["parameters"]["shape"]["point"]["window"].__setitem__("radius", "1/3"),
        )
        with self.assertRaisesRegex(InputValidationError, "hand-over radius"):
            validate_public_parameters(copied)

    def test_changed_pentagon_extension_descriptor_is_rejected(self):
        copied = self.copied_inputs()
        self.rewrite(
            copied,
            "exotic/pentagon.json",
            lambda document: document["parameters"].__setitem__(
                "beyond", {"axis": 0, "inequality": 0}
            ),
        )
        with self.assertRaisesRegex(InputValidationError, "extension descriptor"):
            validate_public_parameters(copied)

    def test_harmless_rational_rewrite_and_key_order_pass(self):
        copied = self.copied_inputs()

        def mutate(document):
            point = document["parameters"]["shape"]["point"]
            point["ratio"] = "2/2"
            # JSON member order is representational only.
            reordered = {key: document[key] for key in reversed(list(document))}
            document.clear()
            document.update(reordered)

        self.rewrite(copied, "exotic/square.json", mutate)
        validate_input_directory(copied)
        validate_public_parameters(copied)


if __name__ == "__main__":
    unittest.main()
