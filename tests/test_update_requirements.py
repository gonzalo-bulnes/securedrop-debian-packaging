import imp
import os
import sys
import pytest
from pathlib import Path


# This below stanza is necessary because the scripts are not
# structured as a module.
path_to_script = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../scripts/update-requirements"
)
sys.path.append(os.path.dirname(path_to_script))
update_requirements = imp.load_source("update-requirements", path_to_script)

TEST_SOURCE_HASH = "8eb170f8d0d61825e09a95b38be068299ddeda82f35e96c3301a8a5e7604cb83"
TEST_WHEEL_HASH = "8e276e2bf50a9a06c36e20f03b050e59b63dfe0678e37164333deb87af03b6ad"
TEST_SHASUM_LINES = ["{}  pathlib2-2.3.2-py2.py3-none-any.whl".format(TEST_WHEEL_HASH),
                     "{}  pathlib2-2.3.2.tar.gz".format(TEST_SOURCE_HASH)]


def test_build_fails_if_sha256_sums_absent(tmpdir, mocker):
    mocker.patch('os.path.exists', return_value=False)

    with pytest.raises(SystemExit) as exc_info:
        update_requirements.verify_sha256sums_file(Path("foo"))

    exit_code = exc_info.value.args[0]
    assert exit_code == 1


def test_build_fails_if_sha256_signature_absent(tmpdir, mocker):
    mocker.patch('os.path.exists', side_effect=[True, False])

    with pytest.raises(SystemExit) as exc_info:
        update_requirements.verify_sha256sums_file(Path("foo"))

    exit_code = exc_info.value.args[0]
    assert exit_code == 1


def test_shasums_skips_sources(tmpdir):
    path_test_shasums = os.path.join(tmpdir, 'test-shasums.txt')
    with open(path_test_shasums, 'w') as f:
        f.writelines(TEST_SHASUM_LINES)

    requirement_name = "pathlib2"
    requirement_version = "2.3.2"
    requirements_lines = ["{}=={}".format(requirement_name, requirement_version)]
    path_result = os.path.join(tmpdir, "test-req.txt")

    update_requirements.add_sha256sums(Path(path_result), requirements_lines, Path(path_test_shasums), Path("foo"))

    with open(path_result, 'r') as f:
        result = f.read()

    assert TEST_WHEEL_HASH in result
    assert TEST_SOURCE_HASH not in result


def test_build_fails_if_missing_wheels(tmpdir):
    path_test_shasums = os.path.join(tmpdir, 'test-shasums.txt')
    with open(path_test_shasums, 'w') as f:
        f.writelines([])

    requirement_name = "pathlib2"
    requirement_version = "2.3.2"
    requirements_lines = ["{}=={}".format(requirement_name, requirement_version)]
    path_result = os.path.join(tmpdir, "test-req.txt")

    with pytest.raises(SystemExit) as exc_info:
        update_requirements.add_sha256sums(Path(path_result), requirements_lines, Path(path_test_shasums), Path("foo"))

    exit_code = exc_info.value.args[0]
    assert exit_code == 1
