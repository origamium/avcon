.PHONY: dev dev-api dev-web build serve

# 開発: API + フロントエンド同時起動
dev:
	@echo "APIサーバーとフロントエンドを起動..."
	$(MAKE) dev-api &
	$(MAKE) dev-web
	@wait

dev-api:
	uv run uvicorn avcon.server:app --reload --port 8000

dev-web:
	cd web && npm run dev

# 本番ビルド
build:
	cd web && npm run build

# 本番配信
serve:
	uv run uvicorn avcon.server:app --host 0.0.0.0 --port 8000
