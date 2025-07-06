"""
Config Reader - 設定ファイル読み込み
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Protocol
from pydantic import BaseModel, Field, ValidationError

# ロギング設定
logger = logging.getLogger(__name__)


class ConfigValidatorProtocol(Protocol):
    """設定バリデーターのプロトコル定義"""

    def validate_config(self, config_data: Dict[str, Any]) -> bool:
        ...


@dataclass
class ConfigReaderConfig:
    """設定読み込み設定のデータクラス"""

    max_retries: int = 3
    retry_delay: float = 1.0
    config_timeout: int = 30
    strict_validation: bool = True


# フェーズ設定のバリデーション用Pydanticモデル
class ThemeConfig(BaseModel):
    name: str = Field(..., description="テーマ名")
    main_question: str = Field(..., description="主要な質問")


class PhaseConfig(BaseModel):
    name: str = Field(..., description="フェーズ名")
    themes: Dict[str, ThemeConfig] = Field(..., description="テーマ設定")


class PhaseConfigFile(BaseModel):
    phase_1: PhaseConfig = Field(..., description="フェーズ1設定")
    phase_2: PhaseConfig = Field(..., description="フェーズ2設定")
    phase_3: PhaseConfig = Field(..., description="フェーズ3設定")
    phase_4: PhaseConfig = Field(..., description="フェーズ4設定")
    phase_5: PhaseConfig = Field(..., description="フェーズ5設定")
    phase_6: PhaseConfig = Field(..., description="フェーズ6設定")
    phase_7: PhaseConfig = Field(..., description="フェーズ7設定")
    phase_8: PhaseConfig = Field(..., description="フェーズ8設定")
    final_phase: PhaseConfig = Field(..., description="最終フェーズ設定")


# システム設定のバリデーション用Pydanticモデル
class SystemConfig(BaseModel):
    project_name: str = Field(..., description="プロジェクト名")
    company_name: str = Field(..., description="企業名")
    industry: str = Field(..., description="業界")
    product_service: str = Field(..., description="製品・サービス")
    target_market: str = Field(..., description="対象市場")
    region: str = Field(..., description="地域")
    competitors: List[str] = Field(default_factory=list, description="競合企業")
    target_customer: str = Field(..., description="ターゲット顧客")
    persona: str = Field(..., description="顧客ペルソナ")
    new_product_idea: str = Field(..., description="新製品アイデア")
    target_user: str = Field(..., description="ターゲットユーザー")
    candidate_countries: str = Field(..., description="候補国")
    brand_name: str = Field(..., description="ブランド名")
    division: str = Field(..., description="事業部")
    main_goal: str = Field(..., description="主要目標")
    budget: str = Field(..., description="予算")
    campaign_objective: str = Field(..., description="キャンペーン目的")
    theme: str = Field(..., description="テーマ")
    objective: str = Field(..., description="目的")
    enable_web_search: bool = Field(default=True, description="Web検索有効化")


class ConfigReader:
    def __init__(
        self,
        validator: Optional[ConfigValidatorProtocol] = None,
        config: Optional[ConfigReaderConfig] = None,
    ) -> None:
        """依存性注入による初期化"""
        self.root_dir = Path(__file__).parent.parent.parent.resolve()
        self.validator = validator
        self.config = config or ConfigReaderConfig()
        self.config_dir = self.root_dir / "config"

    def load_system_config(self) -> Dict[str, Any]:
        """システム設定ファイルの読み込み"""
        config_path = self.config_dir / "system_config.json"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Pydanticによるバリデーション
            if self.config.strict_validation:
                validated_config = SystemConfig(**config_data)
                config_data = validated_config.model_dump()

            logger.info(f"システム設定を読み込みました: {config_data['project_name']}")
            return config_data
        except FileNotFoundError as e:
            logger.error(f"システム設定ファイルが見つかりません: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"システム設定ファイルのJSON形式が不正: {e}")
            raise
        except ValidationError as e:
            logger.error(f"システム設定のバリデーションエラー: {e}")
            raise
        except Exception as e:
            logger.error(f"システム設定の読み込みに失敗: {e}")
            raise

    def load_phase_config(self) -> Dict[str, Any]:
        """フェーズ設定ファイルの読み込み"""
        config_path = self.config_dir / "phase_config.json"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Pydanticによるバリデーション
            if self.config.strict_validation:
                validated_config = PhaseConfigFile(**config_data)
                config_data = validated_config.model_dump()

            logger.info("フェーズ設定を読み込みました")
            return config_data
        except FileNotFoundError as e:
            logger.error(f"フェーズ設定ファイルが見つかりません: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"フェーズ設定ファイルのJSON形式が不正: {e}")
            raise
        except ValidationError as e:
            logger.error(f"フェーズ設定のバリデーションエラー: {e}")
            raise
        except Exception as e:
            logger.error(f"フェーズ設定の読み込みに失敗: {e}")
            raise

    def validate_config_data(self, config_data: Dict[str, Any]) -> bool:
        """設定データの検証"""
        try:
            required_fields = [
                "project_name",
                "company_name",
                "industry",
                "product_service",
                "target_market",
            ]

            missing_fields = []
            for field in required_fields:
                if not config_data.get(field):
                    missing_fields.append(field)

            if missing_fields:
                logger.error(f"必須フィールドが不足しています: {missing_fields}")
                return False

            # カスタムバリデーターがある場合は使用
            if self.validator:
                return self.validator.validate_config(config_data)

            logger.info("設定データの検証が完了しました")
            return True
        except Exception as e:
            logger.error(f"設定データの検証中にエラーが発生: {e}")
            return False

    def get_theme_info(
        self, phase_name: str, theme_id: str
    ) -> Optional[Dict[str, Any]]:
        """特定のテーマ情報を取得"""
        try:
            phase_config = self.load_phase_config()

            if phase_name not in phase_config:
                logger.warning(f"フェーズ {phase_name} が見つかりません")
                return None

            phase_data = phase_config[phase_name]
            if "themes" not in phase_data:
                logger.warning(f"フェーズ {phase_name} にテーマ情報がありません")
                return None

            themes = phase_data["themes"]
            if theme_id not in themes:
                logger.warning(f"テーマ {theme_id} がフェーズ {phase_name} に見つかりません")
                return None

            return themes[theme_id]
        except Exception as e:
            logger.error(f"テーマ情報の取得中にエラーが発生: {e}")
            return None

    def get_all_themes(self) -> Dict[str, Dict[str, Any]]:
        """全テーマ情報を取得"""
        try:
            phase_config = self.load_phase_config()
            all_themes = {}

            for phase_name, phase_data in phase_config.items():
                if isinstance(phase_data, dict) and "themes" in phase_data:
                    for theme_id, theme_info in phase_data["themes"].items():
                        all_themes[f"{phase_name}_{theme_id}"] = {
                            "phase": phase_name,
                            "theme_id": theme_id,
                            "info": theme_info,
                        }

            logger.info(f"全 {len(all_themes)} テーマの情報を取得しました")
            return all_themes
        except Exception as e:
            logger.error(f"全テーマ情報の取得中にエラーが発生: {e}")
            return {}

    def create_sample_config(self) -> Dict[str, Any]:
        """サンプル設定の作成"""
        try:
            sample_config = {
                "project_name": "サンプルプロジェクト",
                "company_name": "サンプル株式会社",
                "industry": "IT・ソフトウェア",
                "product_service": "SaaSプラットフォーム",
                "target_market": "中小企業",
                "region": "日本",
                "competitors": ["競合A", "競合B", "競合C"],
                "target_customer": "中小企業の経営者",
                "persona": "30-50代の中小企業経営者",
                "new_product_idea": "AI活用業務効率化ツール",
                "target_user": "中小企業の従業員",
                "candidate_countries": "日本、東南アジア",
                "brand_name": "サンプルブランド",
                "division": "新規事業部",
                "main_goal": "売上高10億円達成",
                "budget": "1億円",
                "campaign_objective": "ブランド認知度向上",
                "theme": "デジタル変革",
                "objective": "業務効率化",
                "enable_web_search": True,
            }

            logger.info("サンプル設定を作成しました")
            return sample_config
        except Exception as e:
            logger.error(f"サンプル設定の作成中にエラーが発生: {e}")
            return {}

    def save_config(
        self, config_data: Dict[str, Any], config_type: str = "system"
    ) -> bool:
        """設定ファイルの保存"""
        try:
            if config_type == "system":
                config_path = self.config_dir / "system_config.json"
            elif config_type == "phase":
                config_path = self.config_dir / "phase_config.json"
            else:
                logger.error(f"不明な設定タイプ: {config_type}")
                return False

            # バックアップの作成
            if config_path.exists():
                backup_path = config_path.with_suffix(".json.backup")
                with open(config_path, "r", encoding="utf-8") as src:
                    with open(backup_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                logger.debug(f"バックアップを作成: {backup_path}")

            # 設定の保存
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            logger.info(f"{config_type}設定を保存しました: {config_path}")
            return True
        except Exception as e:
            logger.error(f"設定の保存中にエラーが発生: {e}")
            return False

    def get_config_statistics(self) -> Dict[str, Any]:
        """設定統計情報の取得"""
        try:
            stats = {
                "system_config_exists": (
                    self.config_dir / "system_config.json"
                ).exists(),
                "phase_config_exists": (self.config_dir / "phase_config.json").exists(),
                "config_dir": str(self.config_dir),
                "total_themes": len(self.get_all_themes()),
            }

            # システム設定の詳細統計
            if stats["system_config_exists"]:
                system_config = self.load_system_config()
                stats["system_config_fields"] = len(system_config)
                stats["has_competitors"] = bool(system_config.get("competitors"))
                stats["web_search_enabled"] = system_config.get(
                    "enable_web_search", True
                )

            # フェーズ設定の詳細統計
            if stats["phase_config_exists"]:
                phase_config = self.load_phase_config()
                stats["total_phases"] = len(phase_config)
                stats["phases_with_themes"] = sum(
                    1
                    for phase_data in phase_config.values()
                    if isinstance(phase_data, dict) and "themes" in phase_data
                )

            return stats
        except Exception as e:
            logger.error(f"設定統計情報の取得中にエラーが発生: {e}")
            return {"error": str(e)}
