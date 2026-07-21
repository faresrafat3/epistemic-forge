"""Command Line Interface (CLI) for Epistemic Forge.

Provides a rich, self-explanatory terminal experience showing the Neuro-Symbolic 
reasoning process in real-time, without overwhelming the user with raw JSON.
"""
from __future__ import annotations

import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from epistemic_forge.models import ProjectSpec
from epistemic_forge.pipeline.arsenal_run import run_pipeline
from epistemic_forge.memory.economy import budget_manager

console = Console()

def build_parser() -> argparse.ArgumentParser:
    """Constructs the argument parser with standard and Hermes-routing overrides."""
    parser = argparse.ArgumentParser(
        prog="epistemic-forge",
        description="Neuro-Symbolic Agent Framework for deterministic reasoning.",
    )
    # Core Epistemic Arguments
    parser.add_argument("--title", required=True, help="Project title or theme.")
    parser.add_argument("--question", required=True, help="The core research or dialectic question.")
    parser.add_argument("--domain", default="hybrid", help="Reasoning domain (research, philosophy, etc.)")
    
    # Hermes Routing Arguments (Omni-Provider)
    parser.add_argument("--model", default="gpt-4o-mini", help="Provider/Model string (e.g., 'anthropic/claude-3-sonnet').")
    parser.add_argument("--api-base", default=None, help="Custom API Base URL (for Local/vLLM/Ollama).")
    
    return parser

def display_claim_lattice(claims: list):
    """Renders the parsed Claim Lattice as a visual Tree in the terminal."""
    if not claims:
        return
        
    tree = Tree("🌳 [bold blue]Epistemic Claim Lattice[/bold blue]")
    for claim in claims:
        # Pydantic model dump compatibility
        c_dict = claim.model_dump() if hasattr(claim, "model_dump") else claim
        
        claim_node = tree.add(f"[bold white]Claim:[/bold white] {c_dict.get('text', 'Unknown')}")
        
        if c_dict.get("support"):
            support_node = claim_node.add("[green]Supports[/green]")
            for s in c_dict["support"]:
                support_node.add(f"✓ {s}")
                
        if c_dict.get("objections"):
            obj_node = claim_node.add("[red]Objections[/red]")
            for o in c_dict["objections"]:
                obj_node.add(f"✗ {o}")

    console.print(Panel(tree, title="Final Cognitive Structure", border_style="blue"))

def main():
    """Main entrypoint for the CLI."""
    parser = build_parser()
    args = parser.parse_args()

    console.print(f"\n[bold magenta]🧠 Epistemic Forge[/bold magenta] — Initializing Neuro-Symbolic Pipeline")
    console.print(f"[dim]Routing to model: {args.model}[/dim]\n")

    spec = ProjectSpec(
        title=args.title,
        question=args.question,
        domain=args.domain,
        target_model=args.model,
        budget_tokens=8000,
        api_base=args.api_base
    )

    try:
        # Use Rich Progress bar to show deterministic orchestration
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]L2 Conductor is dispatching semantic experts...", total=None)
            
            # Execute the core pipeline
            result = run_pipeline(
                title=spec.title,
                question=spec.question,
                domain=spec.domain.value
                # Note: To fully support Hermes, pipeline/arsenal_run.py must pass target_model down.
            )
            
            progress.update(task, description="[green]Synthesis complete. Crystallizing lattice...[/green]")

        # Render output
        console.print("[bold green]✔ Pipeline Execution Successful.[/bold green]\n")
        
        if hasattr(result, "claims"):
            display_claim_lattice(result.claims)
            
        console.print(f"
[bold yellow]💰 {budget_manager.get_report()}[/bold yellow]")
        else:
            console.print("[yellow]Notice: No claims extracted in the final result.[/yellow]")

    except Exception as e:
        console.print_exception(show_locals=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
