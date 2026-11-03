from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


def configure(evaluator):
    @router.post("/run")
    async def run_evaluation():
        try:
            return evaluator.run()
        except Exception as exc:
            raise HTTPException(500, f"Evaluation failed: {exc}")
    return router
