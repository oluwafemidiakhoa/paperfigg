from __future__ import annotations

import shlex
import subprocess
import time
from typing import Tuple

from paperfig.lab.policy import is_command_allowed
from paperfig.lab.types import LabExperimentResult, LabPolicy


class LabExecutionError(RuntimeError):
    pass


def execute_command(command: str, policy: LabPolicy) -> LabExperimentResult:
    allowed, reason = is_command_allowed(command, policy)
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if not allowed:
        return LabExperimentResult(
            experiment_id="",
            status="failed",
            return_code=126,
            started_at=started_at,
            finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            stdout="",
            stderr="",
            policy_violation=reason,
        )

    try:
        completed = subprocess.run(  # noqa: S603
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=policy.max_runtime_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return LabExperimentResult(
            experiment_id="",
            status="failed",
            return_code=124,
            started_at=started_at,
            finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            stdout=(exc.stdout or "")[:10000],
            stderr=(exc.stderr or "")[:10000],
            policy_violation="execution_timeout",
        )

    status = "completed" if completed.returncode == 0 else "failed"
    return LabExperimentResult(
        experiment_id="",
        status=status,
        return_code=completed.returncode,
        started_at=started_at,
        finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        stdout=completed.stdout[:10000],
        stderr=completed.stderr[:10000],
        policy_violation="",
    )
