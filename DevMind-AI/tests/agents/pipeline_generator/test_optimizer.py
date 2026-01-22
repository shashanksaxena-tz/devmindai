from src.agents.pipeline_generator.optimizer import PipelineOptimizer, OptimizationReport
from src.agents.pipeline_generator.templates import PipelineTemplate, PipelinePlatform

def test_optimize_pipeline():
    optimizer = PipelineOptimizer()
    pipeline = PipelineTemplate(
        platform=PipelinePlatform.GITHUB_ACTIONS,
        content="name: CI\njobs:\n  test:\n    run: pytest",
        filename=".github/workflows/ci.yml"
    )

    optimized, report = optimizer.optimize(pipeline)

    # Check logic from implementation
    assert "Added dependency caching" in report.optimizations_applied
    assert "Parallelized independent jobs" in report.optimizations_applied
    assert report.savings_percentage > 0
    assert report.optimized_estimated_time != report.original_estimated_time

def test_optimize_already_optimized_pipeline():
    optimizer = PipelineOptimizer()
    # Content has cache and needs, so shouldn't add them
    pipeline = PipelineTemplate(
        platform=PipelinePlatform.GITHUB_ACTIONS,
        content="name: CI\njobs:\n  test:\n    cache: pip\n    needs: lint",
        filename=".github/workflows/ci.yml"
    )

    optimized, report = optimizer.optimize(pipeline)

    assert "Added dependency caching" not in report.optimizations_applied
    assert "Parallelized independent jobs" not in report.optimizations_applied
