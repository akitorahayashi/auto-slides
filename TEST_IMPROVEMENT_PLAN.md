# テスト改善 並列作業プラン

## 環境準備完了状況
✅ pytest + 既存fixtureセット  
✅ Mock基盤 (`MockMarpService`, `MockTemplateRepository`, `MockSlideGenerator`)  
✅ テンプレートテストデータ (`tests/templates/k2g4h1x9/`)  
✅ 統合・E2E・UIテスト基盤  

## Mock最適化
- ❌ **削除**: `MockPromptService` (外部依存なし、実サービス使用)
- ❌ **削除**: `MockSlideGeneratorClient` (削除されたプロトコル依存)
- ✅ **保持**: `MockMarpService`, `MockTemplateRepository`, `MockSlideGenerator`

## 並列作業分担（3エージェント）

### 🤖 Agent A (You) - Core Services & Integration
**担当範囲**: サービス層とコア統合テスト
- `tests/unit/services/` 全体リファクタ
- `tests/intg/test_slide_generator_llm.py` LangChain対応
- Mock最適化 (不要Mock削除)
- `conftest.py` fixture更新

**具体タスク**:
1. 不要Mock削除 (`MockPromptService`, `MockSlideGeneratorClient`)
2. `test_slide_generator.py` 新LangChain対応
3. `test_prompt_service.py` 実サービステスト化
4. 統合テスト LangChain chain テスト

### 🤖 Agent B - UI & Component Tests  
**担当範囲**: Streamlit UIテスト
- `tests/ui/` 全体 (4ファイル)
- Streamlitアプリページテスト
- セッション状態管理テスト
- ページ遷移テスト

**具体タスク**:
1. `test_gallery_page.py` - テンプレートギャラリー
2. `test_implementation_page.py` - 実装設定ページ  
3. `test_result_page.py` - 結果表示ページ
4. `test_download_page.py` - ダウンロードページ
5. セッション状態 & ナビゲーションテスト強化

### 🤖 Agent C - Models & E2E Tests
**担当範囲**: モデルテストとE2Eテスト
- `tests/unit/models/` (2ファイル)
- `tests/e2e/` E2Eテスト
- `tests/intg/test_marp_service.py` 統合テスト

**具体タスク**:
1. `test_slide_template.py` モデルテスト強化
2. `test_template_repository.py` リポジトリテスト
3. `test_marp_service_e2e.py` E2Eテスト
4. `test_marp_service.py` 統合テスト強化
5. ファイルI/O・外部依存テスト

## 共通ガイドライン

### テスト品質基準
- カバレッジ85%以上
- 失敗シナリオ含む
- Mock適切使用 (外部依存のみ)
- async/await 適切ハンドリング

### Mock使用方針
- **実サービス使用**: `PromptService` (外部依存なし)
- **Mock使用**: `MarpService` (subprocess), LLM calls, ファイルI/O
- **テストデータ**: 既存 `tests/templates/` 活用

### 完了条件  
- 全テストパス
- 適切なエラーハンドリング
- 非同期処理対応
- リファクタ後の新アーキテクチャ対応

## 作業開始
各エージェントは担当範囲のテストを並列で改善してください。