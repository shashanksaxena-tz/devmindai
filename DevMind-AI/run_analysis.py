#!/usr/bin/env python3
"""
Standalone script to run DevMind-AI analysis on this project.
Runs: 1) Vulnerability Scanner  2) Code Reviewer (limited - no LLM)
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

async def run_vulnerability_scan():
    """Run vulnerability scan on project dependencies."""
    print("\n" + "=" * 60)
    print("🔒 VULNERABILITY SCANNER")
    print("=" * 60)
    
    from src.agents.vuln_scanner.parsers.pip import PipParser
    from src.agents.vuln_scanner.parsers.npm import NpmParser
    from src.agents.vuln_scanner.vuln_db.osv import OSVClient
    
    project_root = Path(__file__).parent
    results = []
    
    # Initialize OSV client
    osv = OSVClient()
    
    try:
        # Check for Python dependencies
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            print(f"\n📦 Found pyproject.toml - parsing Python dependencies...")
            parser = PipParser()
            deps = parser.parse(pyproject.read_text())
            print(f"   Found {len(deps)} Python packages")
            
            if deps:
                # Query OSV for vulnerabilities
                packages = [(d.name, d.version or "0.0.0", "pypi") for d in deps if d.version]
                print(f"   Querying OSV for {len(packages)} packages with versions...")
                
                for name, version, ecosystem in packages[:20]:  # Limit to first 20
                    try:
                        vulns = await osv.query_package(name, version, ecosystem)
                        if vulns:
                            for v in vulns:
                                results.append({
                                    "package": name,
                                    "version": version,
                                    "vuln_id": v.id,
                                    "severity": v.severity,
                                    "title": v.title,
                                    "fixed_version": v.fixed_version
                                })
                    except Exception as e:
                        pass  # Skip individual failures
                
        # Check for Node.js dependencies
        package_json = project_root / "package.json"
        if package_json.exists():
            print(f"\n📦 Found package.json - parsing npm dependencies...")
            parser = NpmParser()
            deps = parser.parse(package_json.read_text())
            print(f"   Found {len(deps)} npm packages")
            
            for d in deps[:20]:  # Limit to first 20
                if d.version:
                    try:
                        vulns = await osv.query_package(d.name, d.version, "npm")
                        if vulns:
                            for v in vulns:
                                results.append({
                                    "package": d.name,
                                    "version": d.version,
                                    "vuln_id": v.id,
                                    "severity": v.severity,
                                    "title": v.title,
                                    "fixed_version": v.fixed_version
                                })
                    except Exception as e:
                        pass
    finally:
        await osv.close()
    
    # Print results
    if results:
        print(f"\n⚠️  Found {len(results)} vulnerabilities:\n")
        for r in results:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠", 
                "medium": "🟡",
                "low": "🟢",
                "unknown": "⚪"
            }.get(r["severity"], "⚪")
            print(f"   {severity_emoji} [{r['severity'].upper()}] {r['package']}@{r['version']}")
            print(f"      ID: {r['vuln_id']}")
            print(f"      Title: {r['title'][:80]}...")
            if r['fixed_version']:
                print(f"      Fix: Upgrade to {r['fixed_version']}")
            print()
    else:
        print("\n✅ No known vulnerabilities found in scanned dependencies!")
    
    return results


def run_code_quality_analysis():
    """Run code quality analysis (debt analyzer components)."""
    print("\n" + "=" * 60)
    print("📊 CODE QUALITY ANALYSIS (Tech Debt)")
    print("=" * 60)
    
    from src.agents.debt_analyzer.complexity import ComplexityAnalyzer
    from src.agents.debt_analyzer.duplication import DuplicationDetector
    
    project_root = Path(__file__).parent / "src"
    
    # Find Python files
    py_files = list(project_root.rglob("*.py"))
    print(f"\n📁 Found {len(py_files)} Python files in src/\n")
    
    # Analyze complexity
    print("📈 Analyzing code complexity...")
    complexity_analyzer = ComplexityAnalyzer()
    high_complexity_files = []
    
    for py_file in py_files:
        try:
            content = py_file.read_text()
            result = complexity_analyzer.analyze(content)
            if result.get("average_complexity", 0) > 5:  # Threshold for complex code
                high_complexity_files.append({
                    "file": str(py_file.relative_to(project_root.parent)),
                    "avg_complexity": result.get("average_complexity", 0),
                    "max_complexity": result.get("max_complexity", 0),
                    "total_functions": result.get("total_functions", 0)
                })
        except Exception:
            pass
    
    if high_complexity_files:
        print(f"\n⚠️  Files with high complexity (>5):")
        for f in sorted(high_complexity_files, key=lambda x: x["avg_complexity"], reverse=True)[:10]:
            print(f"   🔶 {f['file']}")
            print(f"      Avg Complexity: {f['avg_complexity']:.1f}, Max: {f['max_complexity']}, Functions: {f['total_functions']}")
    else:
        print("   ✅ No high-complexity files detected")
    
    # Detect duplication
    print("\n🔄 Detecting code duplication...")
    duplication_detector = DuplicationDetector()
    
    all_contents = {}
    for py_file in py_files:
        try:
            all_contents[str(py_file)] = py_file.read_text()
        except Exception:
            pass
    
    if all_contents:
        duplicates = duplication_detector.detect_duplicates(all_contents, min_lines=6)
        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} potential code duplications:")
            for dup in duplicates[:5]:
                print(f"   📋 {dup.get('description', 'Duplicate block found')}")
        else:
            print("   ✅ No significant code duplication detected")
    
    return {"complexity_issues": len(high_complexity_files)}


async def main():
    print("\n" + "🧠 " * 20)
    print("      DEVMIND-AI ANALYSIS RUNNER")
    print("🧠 " * 20)
    
    # Run vulnerability scan
    vuln_results = await run_vulnerability_scan()
    
    # Run code quality analysis
    quality_results = run_code_quality_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"   🔒 Vulnerabilities found: {len(vuln_results)}")
    print(f"   📊 High-complexity files: {quality_results.get('complexity_issues', 0)}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
