import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import pytest

import dietnb
from dietnb import _core
from matplotlib.figure import Figure


@pytest.fixture(params=["terminal", "zmq", "embed", "qt"], ids=lambda name: f"{name}-shell")
def ipython_shell(request):
    """각 IPython 셸 인스턴스를 생성하고 테스트 후 정리한다."""
    if request.param == "terminal":
        from IPython.terminal.interactiveshell import TerminalInteractiveShell

        shell_cls = TerminalInteractiveShell
    elif request.param == "zmq":
        from ipykernel.zmqshell import ZMQInteractiveShell

        shell_cls = ZMQInteractiveShell
    elif request.param == "embed":
        from IPython.terminal.embed import InteractiveShellEmbed

        shell_cls = InteractiveShellEmbed
    else:
        qtconsole_module = pytest.importorskip(
            "qtconsole.inprocess",
            reason="qtconsole inprocess 지원이 필요합니다."
        )
        manager = qtconsole_module.QtInProcessKernelManager()
        manager.start_kernel()
        shell = manager.kernel.shell
        try:
            yield shell
        finally:
            callbacks = getattr(shell.events, "callbacks", {}).get("post_run_cell")
            if callbacks is not None:
                callbacks.clear()
            for attr in ("iopub_thread", "_default_iopub_thread"):
                thread = getattr(manager.kernel, attr, None)
                if thread is not None:
                    try:
                        thread.stop()
                    except Exception:
                        pass
                    try:
                        thread.close()
                    except Exception:
                        pass
            manager.shutdown_kernel()
        return

    # 신규 인스턴스를 강제로 만들기 위해 기존 싱글턴을 비운다.
    clear_instance = getattr(shell_cls, "clear_instance", None)
    if clear_instance:
        clear_instance()

    shell = shell_cls.instance()
    try:
        yield shell
    finally:
        # 이벤트 핸들러와 싱글턴 상태를 깨끗하게 돌려놓는다.
        callbacks = shell.events.callbacks.get("post_run_cell")
        if callbacks is not None:
            callbacks.clear()
        if clear_instance:
            clear_instance()


@pytest.fixture(autouse=True)
def restore_matplotlib_repr():
    """Figure에 적용된 monkey patch를 테스트 후 원복한다."""
    original_png = getattr(Figure, "_repr_png_", None)
    original_html = getattr(Figure, "_repr_html_", None)
    yield

    if original_png is not None:
        Figure._repr_png_ = original_png
    elif hasattr(Figure, "_repr_png_"):
        del Figure._repr_png_

    if original_html is not None:
        Figure._repr_html_ = original_html
    elif hasattr(Figure, "_repr_html_"):
        del Figure._repr_html_


@pytest.fixture(autouse=True)
def reset_registry_state():
    """_FigureRegistry 전역 상태를 비워 다른 테스트와 간섭을 방지한다."""
    yield
    _core._registry._last_exec_per_cell.clear()
    _core._registry._indices.clear()


@pytest.fixture
def detected_notebook(tmp_path):
    notebook = tmp_path / "sample.ipynb"
    notebook.touch()
    return notebook


@pytest.fixture(autouse=True)
def patch_notebook_detection(monkeypatch, detected_notebook):
    monkeypatch.setattr(_core, "_resolve_notebook_path", lambda _ip: detected_notebook)


@pytest.fixture(autouse=True)
def temp_cwd(tmp_path, monkeypatch):
    """테스트마다 임시 작업 디렉터리를 사용해 생성 파일을 격리한다."""
    monkeypatch.chdir(tmp_path)
    yield


def test_activate_and_deactivate_registers_handlers(ipython_shell):
    """각 셸에서 dietnb.activate / deactivate가 정상 동작하는지 확인한다."""
    shell = ipython_shell
    assert shell.events.callbacks.get("post_run_cell") == []

    dietnb.activate(shell)
    assert _core._patch_applied

    handler = dietnb._post_run_cell_handler
    callbacks = shell.events.callbacks.get("post_run_cell")
    assert handler is not None
    assert callbacks == [handler]
    assert getattr(Figure, "_repr_png_") is _core._no_op_repr_png
    assert callable(getattr(Figure, "_repr_html_"))

    dietnb.deactivate(shell)

    assert dietnb._post_run_cell_handler is None
    assert not _core._patch_applied
    assert shell.events.callbacks.get("post_run_cell") == []


def test_figure_saved_after_activation(ipython_shell, detected_notebook):
    """한 번의 셀 실행에서 생성된 단일 Figure가 파일로 저장되는지 확인한다."""
    shell = ipython_shell
    shell.parent_header = {"metadata": {"cellId": "dietnb-test-cell"}}

    dietnb.activate(shell)
    try:
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        html = fig._repr_html_()
        assert html is not None
        src_attr = html.split('src="')[1].split('"')[0]
        assert not Path(src_attr).is_absolute()
        expected_prefix = f"{detected_notebook.stem}_{_core.DEFAULT_FOLDER_NAME}"
        assert src_attr.startswith(expected_prefix)

        image_dir = _core._get_notebook_image_dir(shell)
        files = list(image_dir.glob("*.png"))
        assert len(files) == 1
        saved_file = files[0]
        assert saved_file.exists()
        assert saved_file.stem.split("_")[0].isdigit()
    finally:
        plt.close(fig)
        dietnb.deactivate(shell)


def test_multiple_figures_in_single_cell_get_unique_indices(ipython_shell, detected_notebook):
    """동일한 셀에서 여러 Figure를 생성해도 파일명이 인덱스로 구분되는지 확인한다."""
    shell = ipython_shell
    shell.parent_header = {"metadata": {"cellId": "dietnb-multi-cell"}}
    shell.execution_count = 7

    dietnb.activate(shell)
    figures = []
    html_outputs = []
    try:
        for offset in range(3):
            fig, ax = plt.subplots()
            ax.plot([0, 1], [offset, offset + 1])
            figures.append(fig)
            html = fig._repr_html_()
            assert html is not None
            html_outputs.append(html)

        image_dir = _core._get_notebook_image_dir(shell)
        files = sorted(image_dir.glob("*.png"))
        assert len(files) == 3

        stems = [f.stem for f in files]
        indices = [stem.split("_")[1] for stem in stems]
        keys = [stem.split("_")[-1] for stem in stems]

        assert indices == ["1", "2", "3"]
        assert len(set(keys)) == 1  # 동일한 셀 키 사용

        digests = []
        for file_path in files:
            data = file_path.read_bytes()
            digests.append(hashlib.sha1(data).hexdigest())
        assert len(set(digests)) == 3  # 이미지 내용도 서로 달라야 한다

        expected_prefix = f"{detected_notebook.stem}_{_core.DEFAULT_FOLDER_NAME}"
        for html in html_outputs:
            src_attr = html.split('src="')[1].split('"')[0]
            assert not Path(src_attr).is_absolute()
            assert src_attr.startswith(expected_prefix)
    finally:
        for fig in figures:
            plt.close(fig)
        dietnb.deactivate(shell)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])