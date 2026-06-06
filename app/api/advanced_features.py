"""
Advanced Features Module for PRETO

Phase 3.3: Advanced Features (Export, Analytics, Recommendations)
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import csv
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)


# ── PDF generation (reportlab) ─────────────────────────────────────────────
def _generate_pdf_report(repositories: List[Dict], title: str = "PRETO Export") -> bytes:
    """Generate a PDF report from repositories using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )

        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()
        teal = colors.HexColor("#00d4b4")
        dark = colors.HexColor("#0b0e14")
        muted = colors.HexColor("#64748b")

        title_style = ParagraphStyle(
            "PRetoTitle", parent=styles["Title"],
            textColor=teal, fontSize=20, spaceAfter=6
        )
        sub_style = ParagraphStyle(
            "PRetoSub", parent=styles["Normal"],
            textColor=muted, fontSize=9, spaceAfter=16
        )
        heading_style = ParagraphStyle(
            "PRetoHeading", parent=styles["Heading2"],
            textColor=teal, fontSize=11, spaceBefore=12, spaceAfter=6
        )
        body_style = ParagraphStyle(
            "PRetoBody", parent=styles["Normal"],
            fontSize=8, textColor=colors.HexColor("#334155")
        )

        elements = []

        # Header
        elements.append(Paragraph("PRETO", title_style))
        elements.append(Paragraph(
            f"{title}  ·  Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            sub_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1, color=teal))
        elements.append(Spacer(1, 0.4*cm))

        # Summary stats
        total_stars = sum(r.get("stargazers_count", 0) for r in repositories)
        total_forks = sum(r.get("forks_count", 0) for r in repositories)
        langs = {}
        for r in repositories:
            if r.get("language"):
                langs[r["language"]] = langs.get(r["language"], 0) + 1

        elements.append(Paragraph("SUMMARY", heading_style))
        summary_data = [
            ["Repositories", "Total Stars", "Total Forks", "Languages"],
            [
                str(len(repositories)),
                f"{total_stars:,}",
                f"{total_forks:,}",
                str(len(langs))
            ]
        ]
        summary_table = Table(summary_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), teal),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.black),
            ("FONTSIZE",    (0, 0), (-1, 0), 8),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 1), (-1, -1), 10),
            ("FONTNAME",    (0, 1), (-1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR",   (0, 1), (-1, -1), teal),
            ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc")]),
            ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("INNERGRID",   (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",  (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0,0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4*cm))

        # Repository table
        elements.append(Paragraph("REPOSITORIES", heading_style))
        headers = ["Repository", "Language", "Stars", "Forks", "Description"]
        col_widths = [5*cm, 2.5*cm, 2*cm, 2*cm, 6*cm]

        table_data = [headers]
        for repo in repositories[:50]:  # Cap at 50 rows
            desc = repo.get("description") or ""
            if len(desc) > 60:
                desc = desc[:57] + "..."
            table_data.append([
                repo.get("name", ""),
                repo.get("language") or "—",
                f"{repo.get('stargazers_count', 0):,}",
                f"{repo.get('forks_count', 0):,}",
                desc,
            ])

        repo_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        repo_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), dark),
            ("TEXTCOLOR",     (0, 0), (-1, 0), teal),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TEXTCOLOR",     (0, 1), (-1, -1), colors.HexColor("#1e293b")),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ]))
        elements.append(repo_table)

        # Footer
        elements.append(Spacer(1, 0.5*cm))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=muted))
        elements.append(Paragraph(
            "Generated by PRETO — Open-source OSINT Intelligence Platform",
            ParagraphStyle("footer", parent=styles["Normal"], fontSize=7, textColor=muted)
        ))

        doc.build(elements)
        return buf.getvalue()

    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")


class AdvancedFeaturesManager:
    """Manages advanced features like export, analytics, and recommendations."""
    
    @staticmethod
    def export_search_results(
        repositories: List[Dict],
        format: str = "json"
    ) -> str:
        """
        Export search results in different formats.
        
        Args:
            repositories: List of repositories to export
            format: Export format (json, csv, pdf)
        
        Returns:
            Exported data as string (or bytes for pdf)
        """
        if format == "csv":
            return AdvancedFeaturesManager._export_csv(repositories)
        elif format == "pdf":
            return _generate_pdf_report(repositories)  # returns bytes
        else:  # json
            return json.dumps(repositories, indent=2, default=str)
    
    @staticmethod
    def _export_csv(repositories: List[Dict]) -> str:
        """Export repositories as CSV."""
        if not repositories:
            return ""
        
        output = StringIO()
        fieldnames = ["name", "full_name", "language", "stargazers_count", "forks_count", "url"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for repo in repositories:
            writer.writerow({
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", ""),
                "language": repo.get("language", ""),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "url": repo.get("html_url", "")
            })
        
        return output.getvalue()
    
    @staticmethod
    def generate_analytics(
        repositories: List[Dict],
        period_days: int = 30
    ) -> Dict:
        """
        Generate analytics from repositories.
        
        Args:
            repositories: List of repositories
            period_days: Analysis period
        
        Returns:
            Analytics dictionary
        """
        if not repositories:
            return {
                "total_repos": 0,
                "total_stars": 0,
                "total_forks": 0,
                "analytics": {}
            }
        
        total_repos = len(repositories)
        total_stars = sum(r.get("stargazers_count", 0) for r in repositories)
        total_forks = sum(r.get("forks_count", 0) for r in repositories)
        total_watchers = sum(r.get("watchers_count", 0) for r in repositories)
        
        # Language distribution
        languages = {}
        for repo in repositories:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        # Top repositories
        top_repos = sorted(
            repositories,
            key=lambda x: x.get("stargazers_count", 0),
            reverse=True
        )[:5]
        
        # Trending (recent updates)
        trending = sorted(
            repositories,
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )[:5]
        
        return {
            "total_repos": total_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_watchers": total_watchers,
            "average_stars_per_repo": total_stars // total_repos if total_repos > 0 else 0,
            "average_forks_per_repo": total_forks // total_repos if total_repos > 0 else 0,
            "languages": languages,
            "top_repos": [
                {
                    "name": r.get("name"),
                    "stars": r.get("stargazers_count", 0)
                }
                for r in top_repos
            ],
            "trending": [
                {
                    "name": r.get("name"),
                    "updated_at": r.get("updated_at")
                }
                for r in trending
            ]
        }
    
    @staticmethod
    def get_recommendations(
        search_history: List[Dict],
        repositories: List[Dict]
    ) -> List[Dict]:
        """
        Generate recommendations based on search history and data.
        
        Args:
            search_history: User's search history
            repositories: Available repositories
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not repositories:
            return recommendations
        
        # Get most searched languages
        language_searches = {}
        for search in search_history[-10:]:  # Last 10 searches
            if "language" in search:
                lang = search["language"]
                language_searches[lang] = language_searches.get(lang, 0) + 1
        
        # Recommend similar to top searches
        if language_searches:
            top_language = max(language_searches, key=language_searches.get)
            
            # Find high-star repos in that language
            similar = [
                r for r in repositories
                if r.get("language") == top_language and r.get("stargazers_count", 0) > 1000
            ][:5]
            
            recommendations.extend([
                {
                    "type": "language_match",
                    "repository": r.get("name"),
                    "reason": f"You frequently search for {top_language} projects",
                    "stars": r.get("stargazers_count", 0)
                }
                for r in similar
            ])
        
        # Trending recommendations
        trending = sorted(
            repositories,
            key=lambda x: x.get("stargazers_count", 0),
            reverse=True
        )[:3]
        
        for repo in trending:
            recommendations.append({
                "type": "trending",
                "repository": repo.get("name"),
                "reason": "Currently trending on GitHub",
                "stars": repo.get("stargazers_count", 0)
            })
        
        return recommendations[:10]
    
    @staticmethod
    def generate_report(
        user_id: int,
        search_history: List[Dict],
        repositories: List[Dict],
        analytics: Dict
    ) -> Dict:
        """
        Generate comprehensive user report.
        
        Args:
            user_id: User ID
            search_history: User's search history
            repositories: User's repositories
            analytics: Analytics data
        
        Returns:
            Comprehensive report
        """
        recommendations = AdvancedFeaturesManager.get_recommendations(
            search_history,
            repositories
        )
        
        report = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_searches": len(search_history),
                "total_repositories_analyzed": analytics.get("total_repos", 0),
                "total_stars_analyzed": analytics.get("total_stars", 0)
            },
            "analytics": analytics,
            "recommendations": recommendations,
            "top_languages": list(analytics.get("languages", {}).keys())[:5],
            "report_sections": [
                "summary",
                "analytics",
                "recommendations",
                "trends"
            ]
        }
        
        return report
    
    @staticmethod
    def compare_repositories(
        repo_list_1: List[Dict],
        repo_list_2: List[Dict]
    ) -> Dict:
        """
        Compare two lists of repositories.
        
        Args:
            repo_list_1: First repository list
            repo_list_2: Second repository list
        
        Returns:
            Comparison metrics
        """
        stats_1 = AdvancedFeaturesManager.generate_analytics(repo_list_1)
        stats_2 = AdvancedFeaturesManager.generate_analytics(repo_list_2)
        
        return {
            "list_1": {
                "count": len(repo_list_1),
                "total_stars": stats_1["total_stars"],
                "avg_stars": stats_1["average_stars_per_repo"]
            },
            "list_2": {
                "count": len(repo_list_2),
                "total_stars": stats_2["total_stars"],
                "avg_stars": stats_2["average_stars_per_repo"]
            },
            "comparison": {
                "more_repos_in_list": "1" if len(repo_list_1) > len(repo_list_2) else "2",
                "higher_total_stars_in_list": "1" if stats_1["total_stars"] > stats_2["total_stars"] else "2",
                "higher_avg_quality_in_list": "1" if stats_1["average_stars_per_repo"] > stats_2["average_stars_per_repo"] else "2"
            }
        }


def get_advanced_features_manager() -> AdvancedFeaturesManager:
    """Get advanced features manager."""
    return AdvancedFeaturesManager()
