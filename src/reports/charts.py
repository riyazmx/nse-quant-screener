from __future__ import annotations

import logging
from pathlib import Path
from typing import Any


def _write_empty_chart_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def _save_placeholder_chart(path: Path, title: str, logger: logging.Logger) -> None:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 4))
    plt.title(title)
    plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.warning("Created placeholder chart: %s", path.name)


def generate_charts(ranked_stocks: Any, charts_dir: Path, logger: logging.Logger) -> dict[str, Path]:
    """Generate all required Phase 3 charts."""
    charts_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "pe_hist_top_industries": charts_dir / "pe_hist_top_industries.png",
        "pe_discount_vs_roe": charts_dir / "pe_discount_vs_roe.png",
        "value_vs_momentum": charts_dir / "value_vs_momentum.png",
        "sector_avg_total_score": charts_dir / "sector_avg_total_score.png",
        "top20_total_score": charts_dir / "top20_total_score.png",
    }

    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        logger.warning("Matplotlib unavailable (%s). Writing empty chart files.", exc)
        for path in files.values():
            _write_empty_chart_file(path)
        return files

    if ranked_stocks is None or getattr(ranked_stocks, "empty", True):
        for name, path in files.items():
            _save_placeholder_chart(path, name.replace("_", " ").title(), logger)
        return files

    # 1) PE histogram top industries
    if {"industry", "pe"}.issubset(ranked_stocks.columns):
        top_industries = ranked_stocks["industry"].value_counts().head(5).index
        subset = ranked_stocks[ranked_stocks["industry"].isin(top_industries)]
        plt.figure(figsize=(10, 6))
        for industry in top_industries:
            values = subset.loc[subset["industry"] == industry, "pe"].dropna()
            if not values.empty:
                plt.hist(values, bins=15, alpha=0.4, label=industry)
        plt.title("PE Histogram: Top Industries")
        plt.xlabel("PE")
        plt.ylabel("Count")
        plt.legend()
        plt.tight_layout()
        plt.savefig(files["pe_hist_top_industries"])
        plt.close()
    else:
        _save_placeholder_chart(files["pe_hist_top_industries"], "PE Histogram: Top Industries", logger)

    # 2) PE discount vs ROE
    if {"pe_discount", "roe"}.issubset(ranked_stocks.columns):
        plt.figure(figsize=(8, 6))
        plt.scatter(ranked_stocks["pe_discount"], ranked_stocks["roe"], alpha=0.7)
        plt.title("PE Discount vs ROE")
        plt.xlabel("PE Discount")
        plt.ylabel("ROE")
        plt.tight_layout()
        plt.savefig(files["pe_discount_vs_roe"])
        plt.close()
    else:
        _save_placeholder_chart(files["pe_discount_vs_roe"], "PE Discount vs ROE", logger)

    # 3) Value vs momentum
    if {"value_score", "momentum_score"}.issubset(ranked_stocks.columns):
        plt.figure(figsize=(8, 6))
        plt.scatter(ranked_stocks["value_score"], ranked_stocks["momentum_score"], alpha=0.7)
        plt.title("Value Score vs Momentum Score")
        plt.xlabel("Value Score")
        plt.ylabel("Momentum Score")
        plt.tight_layout()
        plt.savefig(files["value_vs_momentum"])
        plt.close()
    else:
        _save_placeholder_chart(files["value_vs_momentum"], "Value Score vs Momentum Score", logger)

    # 4) Sector avg total score
    if {"sector", "total_score"}.issubset(ranked_stocks.columns):
        sector_avg = (
            ranked_stocks.groupby("sector", as_index=False)["total_score"]
            .mean()
            .sort_values("total_score", ascending=False)
        )
        plt.figure(figsize=(10, 6))
        plt.bar(sector_avg["sector"], sector_avg["total_score"])
        plt.title("Sector Average Total Score")
        plt.xlabel("Sector")
        plt.ylabel("Average Total Score")
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        plt.savefig(files["sector_avg_total_score"])
        plt.close()
    else:
        _save_placeholder_chart(files["sector_avg_total_score"], "Sector Average Total Score", logger)

    # 5) Top 20 total score
    if {"symbol", "total_score"}.issubset(ranked_stocks.columns):
        top20 = ranked_stocks.sort_values("total_score", ascending=False).head(20)
        plt.figure(figsize=(12, 6))
        plt.bar(top20["symbol"], top20["total_score"])
        plt.title("Top 20 Total Score")
        plt.xlabel("Symbol")
        plt.ylabel("Total Score")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(files["top20_total_score"])
        plt.close()
    else:
        _save_placeholder_chart(files["top20_total_score"], "Top 20 Total Score", logger)

    return files
