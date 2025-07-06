"""
Quality Checker - レポート品質チェック
"""
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass

# ロギング設定
logger = logging.getLogger(__name__)


class QualityValidatorProtocol(Protocol):
    """品質バリデーターのプロトコル定義"""

    def validate_quality(self, content: str) -> Dict[str, Any]:
        ...


@dataclass
class QualityConfig:
    """品質チェック設定のデータクラス"""

    min_word_count: int = 3000
    min_sources: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0
    strict_validation: bool = True


class QualityChecker:
    def __init__(
        self,
        validator: Optional[QualityValidatorProtocol] = None,
        config: Optional[QualityConfig] = None,
    ) -> None:
        """依存性注入による初期化"""
        self.root_dir = Path(__file__).parent.parent.parent.resolve()
        self.validator = validator
        self.config = config or QualityConfig()
        self.required_sections = ["現状分析", "戦略提言", "実行計画", "参考文献"]

    def check_report(self, report_path: Path) -> Dict[str, Any]:
        """レポートの品質チェック"""
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()

            results = {
                "passed": True,
                "score": 100,
                "issues": [],
                "warnings": [],
                "recommendations": [],
            }

            # 文字数チェック
            word_count = self._count_words(content)
            if word_count < self.config.min_word_count:
                results["passed"] = False
                results["score"] -= 20
                results["issues"].append(
                    f"文字数が不足しています ({word_count}/{self.config.min_word_count})"
                )
            else:
                results["recommendations"].append(f"文字数は十分です ({word_count}文字)")

            # 情報源チェック
            sources_count = self._count_sources(content)
            if sources_count < self.config.min_sources:
                results["passed"] = False
                results["score"] -= 15
                results["issues"].append(
                    f"情報源が不足しています ({sources_count}/{self.config.min_sources})"
                )
            else:
                results["recommendations"].append(f"情報源は十分です ({sources_count}件)")

            # 必須セクションチェック
            missing_sections = self._check_required_sections(content)
            if missing_sections:
                results["passed"] = False
                results["score"] -= 10 * len(missing_sections)
                results["issues"].append(f"必須セクションが不足: {', '.join(missing_sections)}")
            else:
                results["recommendations"].append("すべての必須セクションが含まれています")

            # 構造チェック
            structure_score = self._check_structure(content)
            results["score"] += structure_score
            if structure_score < 0:
                results["warnings"].append("レポート構造の改善が必要です")

            # 内容品質チェック
            content_score = self._check_content_quality(content)
            results["score"] += content_score
            if content_score < 0:
                results["warnings"].append("内容の品質向上が必要です")

            # スコアの正規化
            results["score"] = max(0, min(100, results["score"]))

            # カスタムバリデーターがある場合は使用
            if self.validator:
                custom_result = self.validator.validate_quality(content)
                results.update(custom_result)

            logger.info(f"品質チェック完了: スコア {results['score']}/100")
            return results
        except FileNotFoundError as e:
            logger.error(f"レポートファイルが見つかりません: {report_path}")
            return {
                "passed": False,
                "score": 0,
                "issues": [f"ファイルが見つかりません: {e}"],
                "warnings": [],
                "recommendations": [],
            }
        except Exception as e:
            logger.error(f"品質チェック中にエラーが発生: {e}")
            return {
                "passed": False,
                "score": 0,
                "issues": [f"品質チェックエラー: {e}"],
                "warnings": [],
                "recommendations": [],
            }

    def _count_words(self, content: str) -> int:
        """文字数のカウント"""
        try:
            # 日本語と英語の単語をカウント
            japanese_words = len(
                re.findall(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+", content)
            )
            english_words = len(re.findall(r"\b[a-zA-Z]+\b", content))
            return japanese_words + english_words
        except Exception as e:
            logger.error(f"文字数カウント中にエラーが発生: {e}")
            return 0

    def _count_sources(self, content: str) -> int:
        """情報源のカウント"""
        try:
            # URLパターンを検索
            url_pattern = r"https?://[^\s\)]+"
            urls = re.findall(url_pattern, content)

            # 引用パターンを検索
            citation_pattern = r"\[(\d+)\].*?(https?://[^\s\)]+)"
            citations = re.findall(citation_pattern, content)

            # 参考文献セクションを検索
            references_section = re.search(r"## 参考文献.*?(?=##|$)", content, re.DOTALL)
            reference_count = 0
            if references_section:
                reference_lines = references_section.group(0).split("\n")
                reference_count = len(
                    [
                        line
                        for line in reference_lines
                        if line.strip() and not line.startswith("#")
                    ]
                )

            total_sources = len(set(urls)) + len(set(citations)) + reference_count
            return total_sources
        except Exception as e:
            logger.error(f"情報源カウント中にエラーが発生: {e}")
            return 0

    def _check_required_sections(self, content: str) -> List[str]:
        """必須セクションのチェック"""
        try:
            missing_sections = []

            for section in self.required_sections:
                if section not in content:
                    missing_sections.append(section)

            return missing_sections
        except Exception as e:
            logger.error(f"必須セクションチェック中にエラーが発生: {e}")
            return self.required_sections

    def _check_structure(self, content: str) -> int:
        """レポート構造のチェック"""
        try:
            score = 0

            # 見出しレベルのチェック
            headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)
            heading_levels = [len(h[0]) for h in headings]

            # 適切な見出し階層があるかチェック
            if len(set(heading_levels)) >= 3:
                score += 5
            else:
                score -= 5

            # 目次の存在チェック
            if "## 目次" in content or "## 目次" in content:
                score += 3
            else:
                score -= 3

            # エグゼクティブサマリーの存在チェック
            if "## エグゼクティブサマリー" in content or "## サマリー" in content:
                score += 2
            else:
                score -= 2

            return score
        except Exception as e:
            logger.error(f"構造チェック中にエラーが発生: {e}")
            return 0

    def _check_content_quality(self, content: str) -> int:
        """内容品質のチェック"""
        try:
            score = 0

            # 図表の存在チェック
            if "|" in content and "---" in content:  # テーブルの存在
                score += 3

            # 箇条書きの存在チェック
            bullet_points = len(re.findall(r"^\s*[-*+]\s+", content, re.MULTILINE))
            if bullet_points >= 10:
                score += 2
            elif bullet_points >= 5:
                score += 1
            else:
                score -= 2

            # 数値データの存在チェック
            numbers = len(re.findall(r"\d+%|\d+円|\d+万円|\d+億円|\d+社|\d+人", content))
            if numbers >= 5:
                score += 3
            elif numbers >= 2:
                score += 1
            else:
                score -= 3

            # 専門用語の使用チェック
            business_terms = ["戦略", "分析", "市場", "競合", "顧客", "収益", "コスト", "ROI", "KPI"]
            term_count = sum(1 for term in business_terms if term in content)
            if term_count >= 5:
                score += 2
            elif term_count >= 3:
                score += 1
            else:
                score -= 2

            return score
        except Exception as e:
            logger.error(f"内容品質チェック中にエラーが発生: {e}")
            return 0

    def generate_quality_report(self, report_path: Path) -> Dict[str, Any]:
        """詳細な品質レポートの生成"""
        try:
            quality_result = self.check_report(report_path)

            report = {
                "file_path": str(report_path),
                "file_size": report_path.stat().st_size if report_path.exists() else 0,
                "quality_score": quality_result["score"],
                "passed": quality_result["passed"],
                "detailed_analysis": {
                    "word_count": self._count_words(
                        open(report_path, "r", encoding="utf-8").read()
                    )
                    if report_path.exists()
                    else 0,
                    "source_count": self._count_sources(
                        open(report_path, "r", encoding="utf-8").read()
                    )
                    if report_path.exists()
                    else 0,
                    "structure_score": self._check_structure(
                        open(report_path, "r", encoding="utf-8").read()
                    )
                    if report_path.exists()
                    else 0,
                    "content_score": self._check_content_quality(
                        open(report_path, "r", encoding="utf-8").read()
                    )
                    if report_path.exists()
                    else 0,
                },
                "issues": quality_result["issues"],
                "warnings": quality_result["warnings"],
                "recommendations": quality_result["recommendations"],
                "improvement_suggestions": self._generate_improvement_suggestions(
                    quality_result
                ),
            }

            return report
        except Exception as e:
            logger.error(f"品質レポート生成中にエラーが発生: {e}")
            return {
                "error": str(e),
                "file_path": str(report_path),
                "quality_score": 0,
                "passed": False,
            }

    def _generate_improvement_suggestions(
        self, quality_result: Dict[str, Any]
    ) -> List[str]:
        """改善提案の生成"""
        try:
            suggestions = []

            if quality_result["score"] < 70:
                suggestions.append("全体的な品質向上が必要です。より詳細な分析と具体的なデータを含めてください。")

            if any("文字数" in issue for issue in quality_result["issues"]):
                suggestions.append("より詳細な分析を追加し、文字数を増やしてください。")

            if any("情報源" in issue for issue in quality_result["issues"]):
                suggestions.append("信頼できる情報源を追加し、引用を適切に行ってください。")

            if any("セクション" in issue for issue in quality_result["issues"]):
                suggestions.append("必須セクションを追加し、レポート構造を完成させてください。")

            if quality_result["warnings"]:
                suggestions.append("レポート構造と内容品質の改善を行ってください。")

            if not suggestions:
                suggestions.append("レポートの品質は良好です。継続的な改善を心がけてください。")

            return suggestions
        except Exception as e:
            logger.error(f"改善提案生成中にエラーが発生: {e}")
            return ["改善提案の生成中にエラーが発生しました。"]

    def batch_check_reports(self, report_dir: Path) -> Dict[str, Any]:
        """複数レポートの一括品質チェック"""
        try:
            if not report_dir.exists():
                logger.error(f"レポートディレクトリが見つかりません: {report_dir}")
                return {"error": f"ディレクトリが見つかりません: {report_dir}"}

            report_files = list(report_dir.glob("**/*.md"))
            results = {
                "total_reports": len(report_files),
                "passed_reports": 0,
                "failed_reports": 0,
                "average_score": 0,
                "reports": [],
            }

            total_score = 0

            for report_file in report_files:
                try:
                    quality_result = self.check_report(report_file)
                    report_info = {
                        "file_path": str(report_file),
                        "quality_score": quality_result["score"],
                        "passed": quality_result["passed"],
                        "issues": quality_result["issues"],
                    }

                    results["reports"].append(report_info)
                    total_score += quality_result["score"]

                    if quality_result["passed"]:
                        results["passed_reports"] += 1
                    else:
                        results["failed_reports"] += 1

                except Exception as e:
                    logger.error(f"レポート {report_file} のチェック中にエラーが発生: {e}")
                    results["reports"].append(
                        {
                            "file_path": str(report_file),
                            "quality_score": 0,
                            "passed": False,
                            "issues": [f"チェックエラー: {e}"],
                        }
                    )
                    results["failed_reports"] += 1

            if results["total_reports"] > 0:
                results["average_score"] = total_score / results["total_reports"]

            logger.info(
                f"一括品質チェック完了: {results['passed_reports']}/{results['total_reports']} レポートが合格"
            )
            return results
        except Exception as e:
            logger.error(f"一括品質チェック中にエラーが発生: {e}")
            return {"error": str(e)}

    def get_quality_statistics(self) -> Dict[str, Any]:
        """品質チェック統計情報の取得"""
        try:
            stats = {
                "config": {
                    "min_word_count": self.config.min_word_count,
                    "min_sources": self.config.min_sources,
                    "required_sections": self.required_sections,
                    "strict_validation": self.config.strict_validation,
                },
                "validator_available": self.validator is not None,
            }

            return stats
        except Exception as e:
            logger.error(f"品質統計情報の取得中にエラーが発生: {e}")
            return {"error": str(e)}
