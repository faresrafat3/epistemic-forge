with open("epistemic_forge/pipeline/arsenal_run.py", "r") as f:
    content = f.read()

if "from loguru import logger" not in content:
    content = "from loguru import logger\n" + content

old_run = "    return ArsenalRun.create().run(spec)"
new_run = """    try:
        logger.info(f"Starting Epistemic Forge Pipeline for: '{title}'")
        result = ArsenalRun.create().run(spec)
        logger.success("Pipeline execution completed successfully.")
        return result
    except Exception as e:
        logger.exception(f"Critical Pipeline Failure: {str(e)}")
        raise SystemExit(1)"""

if old_run in content:
    content = content.replace(old_run, new_run)

with open("epistemic_forge/pipeline/arsenal_run.py", "w") as f:
    f.write(content)
