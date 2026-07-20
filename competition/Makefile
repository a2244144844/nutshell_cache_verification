# ============================================================================
# UCAgent Track1 Cache Verification — Makefile
# ============================================================================
# Wraps competition/scripts/*.sh with a standardised make interface.
# All heavy lifting is delegated to bash scripts; this file only provides
# discoverability, parameterisation, and shortcut targets.
#
# Quick start:
#   make             → 显示帮助
#   make reproduce   → 一键复现全流程
#   make test        → 回归测试
#   make coverage    → 覆盖率报告
# ============================================================================

SHELL  := /bin/bash
MAKEFLAGS += --no-print-directory

# — Paths ————————————————————————————————————————————————————————————————
ROOT_DIR    := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SCRIPT_DIR  := $(ROOT_DIR)/scripts
VENV_PYTHON := $(ROOT_DIR)/../.venv/bin/python

# — User-overridable parameters ——————————————————————————————————————————
SEED  ?= 7
STEPS ?= 18
STAGE ?= 1

# — Colour helpers ————————————————————————————————————————————————————————
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RESET  := \033[0m

# ============================================================================
# Default target
# ============================================================================
.DEFAULT_GOAL := help

# ============================================================================
# Self-documentation
# ============================================================================
help: ## 显示此帮助信息
	@echo ""
	@echo "$(GREEN)UCAgent Track1 Cache Verification$(RESET)"
	@echo "$(GREEN)==================================$(RESET)"
	@echo ""
	@echo "$(YELLOW)入口命令:$(RESET)"
	@echo "  make reproduce      一键复现全流程 (clean → regression → coverage → bug)"
	@echo "  make quick           快速验证 (clean → export → smoke)"
	@echo ""
	@echo "$(YELLOW)测试:$(RESET)"
	@echo "  make test            完整回归测试 (smoke + directed + corner)"
	@echo "  make test-smoke      仅冒烟测试"
	@echo "  make test-directed   仅定向测试"
	@echo "  make test-corner     仅角落测试"
	@echo "  make test-random     随机测试 (可覆盖 SEED / STEPS)"
	@echo ""
	@echo "$(YELLOW)覆盖率:$(RESET)"
	@echo "  make coverage        收集覆盖率报告 (单种子)"
	@echo "  make coverage-multi  多种子覆盖率 (10 seeds × 200 steps)"
	@echo "  make view-coverage   在浏览器中打开 RTL 覆盖率 HTML"
	@echo ""
	@echo "$(YELLOW)Bug 注入:$(RESET)"
	@echo "  make bug-inject      运行 bug 注入 (预期失败)"
	@echo "  make bug-recover     恢复路径验证 (--disable-bug)"
	@echo ""
	@echo "$(YELLOW)UCAgent:$(RESET)"
	@echo "  make stage           运行指定阶段 (用法: make stage STAGE=5)"
	@echo ""
	@echo "$(YELLOW)清理:$(RESET)"
	@echo "  make clean           清理构建产物 / 缓存 / 波形"
	@echo "  make distclean        深度清理"
	@echo ""
	@echo "$(YELLOW)其他:$(RESET)"
	@echo "  make export          仅导出 DUT (Picker → Python)"
	@echo "  make vars            显示当前可覆盖变量"
	@echo ""

# ============================================================================
# 清理
# ============================================================================
clean: ## 清理构建产物、缓存、波形文件
	bash "$(SCRIPT_DIR)/clean_generated.sh"

distclean: clean ## 深度清理 (含 build/ 目录)
	rm -rf "$(ROOT_DIR)/build"
	rm -f "$(ROOT_DIR)/cache.vcd"
	rm -f "$(ROOT_DIR)/VCache_coverage.dat"
	rm -f "$(ROOT_DIR)/VAdder_coverage.dat"
	find "$(ROOT_DIR)" -name ".pytest_cache" -type d -prune -exec rm -rf {} +
	find "$(ROOT_DIR)" -name "__pycache__" -type d -prune -exec rm -rf {} +
	@echo "[distclean] 深度清理完成"

# ============================================================================
# DUT 导出
# ============================================================================
export: ## 导出 DUT (Picker export)
	bash "$(SCRIPT_DIR)/export_cache_dut.sh"

# ============================================================================
# 测试
# ============================================================================
test: ## 完整回归测试 (smoke + directed + corner)
	bash "$(SCRIPT_DIR)/run_regression.sh"

test-smoke: ## 仅冒烟测试
	bash "$(SCRIPT_DIR)/run_smoke.sh"

test-directed: ## 仅定向测试
	bash "$(SCRIPT_DIR)/run_directed.sh"

test-corner: ## 仅角落测试 (反压)
	bash "$(SCRIPT_DIR)/export_cache_dut.sh"
	source "$(SCRIPT_DIR)/env.sh" && \
		export PYTHONPATH="$(ROOT_DIR):$${PYTHONPATH:-}" && \
		$(VENV_PYTHON) -m pytest "$(ROOT_DIR)/tests/corner" -q

test-random: ## 随机测试 (用法: make test-random SEED=42 STEPS=200)
	bash "$(SCRIPT_DIR)/run_random.sh" $(SEED) $(STEPS)

# ============================================================================
# 覆盖率
# ============================================================================
coverage: ## 收集覆盖率报告 (可覆盖: SEED=42 STEPS=200)
	bash "$(SCRIPT_DIR)/collect_coverage.sh" $(SEED) $(STEPS)

coverage-multi: ## 多种子覆盖率 (10 seeds × 200 steps)
	bash "$(SCRIPT_DIR)/collect_coverage_multi.sh"

view-coverage: ## 在浏览器中打开 RTL 覆盖率 HTML
	@if [ -f "$(ROOT_DIR)/build/reports/rtl_coverage.html" ]; then \
		open "$(ROOT_DIR)/build/reports/rtl_coverage.html"; \
	else \
		echo "rtl_coverage.html 不存在，请先运行 make coverage 或 make coverage-multi"; \
	fi

# ============================================================================
# Bug 注入
# ============================================================================
bug-inject: ## 运行 bug 注入 (预期失败 — 验证 scoreboard 检测能力)
	bash "$(SCRIPT_DIR)/run_bug_injection.sh"

bug-recover: ## 恢复路径验证 (--disable-bug)
	bash "$(SCRIPT_DIR)/run_bug_injection.sh" --disable-bug

# ============================================================================
# 一键复现
# ============================================================================
reproduce: ## 一键复现全流程 (clean → regression → coverage → bug)
	@echo "╔══════════════════════════════════════════════╗"
	@echo "║  UCAgent Track1 Cache — 一键复现全流程       ║"
	@echo "╚══════════════════════════════════════════════╝"
	@echo ""
	@echo "[1/4] 清理旧产物 …"
	bash "$(SCRIPT_DIR)/clean_generated.sh"
	@echo ""
	@echo "[2/4] 运行回归测试 …"
	bash "$(SCRIPT_DIR)/run_regression.sh"
	@echo ""
	@echo "[3/4] 收集覆盖率 …"
	bash "$(SCRIPT_DIR)/collect_coverage.sh" $(SEED) $(STEPS)
	@echo ""
	@echo "[4/4] bug 注入验证 …"
	@echo "  (a) bug 注入 (预期失败) …"
	@bash "$(SCRIPT_DIR)/run_bug_injection.sh" && { \
		echo "ERROR: bug injection unexpectedly passed!" >&2; \
		exit 1; \
	} || true
	@echo "  (b) 恢复路径验证 …"
	bash "$(SCRIPT_DIR)/run_bug_injection.sh" --disable-bug
	@echo ""
	@echo "╔══════════════════════════════════════════════╗"
	@echo "║  ✓ 全流程复现通过                             ║"
	@echo "╚══════════════════════════════════════════════╝"

quick: clean export ## 快速验证 (清理 → 导出 → 冒烟)
	bash "$(SCRIPT_DIR)/run_smoke.sh"

# ============================================================================
# UCAgent Stage
# ============================================================================
stage: ## 运行指定 UCAgent 阶段 (用法: make stage STAGE=5)
	bash "$(SCRIPT_DIR)/run_ucagent_stage.sh" $(STAGE)

# ============================================================================
# 变量展示
# ============================================================================
vars: ## 显示当前可覆盖变量及默认值
	@echo "SEED  = $(SEED)    (随机测试种子, 默认 7)"
	@echo "STEPS = $(STEPS)   (随机测试步数, 默认 18)"
	@echo "STAGE = $(STAGE)    (UCAgent stage 索引, 默认 1)"
	@echo ""
	@echo "覆盖示例:"
	@echo "  make test-random SEED=42 STEPS=200"
	@echo "  make stage STAGE=5"
	@echo "  make coverage SEED=13 STEPS=50"

# ============================================================================
# 快捷方式
# ============================================================================
smoke:      test-smoke      ## 快捷方式 → make test-smoke
directed:   test-directed   ## 快捷方式 → make test-directed
corner:     test-corner     ## 快捷方式 → make test-corner
random:     test-random     ## 快捷方式 → make test-random
regression: test            ## 快捷方式 → make test
cov:        coverage        ## 快捷方式 → make coverage

# ============================================================================
# Phony targets (must be at end so pattern matching is unaffected)
# ============================================================================
.PHONY: help clean distclean export \
        test test-smoke test-directed test-corner test-random \
        coverage coverage-multi view-coverage \
        bug-inject bug-recover reproduce quick \
        stage vars \
        smoke directed corner random regression cov
