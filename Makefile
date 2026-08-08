# ABOUTME: Makefile for managing Claude Code configuration symlinks.
# ABOUTME: Creates individual symlinks for skills, agents, etc. to allow third-party additions.

# Claude Code Configuration Manager
# Usage: make install | make uninstall | make status | make help

SHELL := /bin/bash
SOURCE_DIR := $(shell pwd)
TARGET_DIR := $(HOME)/.claude

# Directories to create and populate with symlinks
DIRS := skills agents commands docs scripts output-styles

# Individual files to symlink
FILES := CLAUDE.md statusline-command.sh

.PHONY: help install uninstall status clean dirs prune

help:
	@echo "Claude Code Config Manager"
	@echo ""
	@echo "Targets:"
	@echo "  make install   - Create symlinks for managed config"
	@echo "  make uninstall - Remove managed symlinks (keeps third-party)"
	@echo "  make status    - Show what's managed vs third-party"
	@echo "  make clean     - Full uninstall (removes all symlinks)"
	@echo ""
	@echo "Source: $(SOURCE_DIR)"
	@echo "Target: $(TARGET_DIR)"

install: dirs
	@echo "Installing symlinks..."
	@# Symlink individual items in each directory
	@for dir in $(DIRS); do \
		if [ -d "$(SOURCE_DIR)/$$dir" ]; then \
			for item in $(SOURCE_DIR)/$$dir/*; do \
				[ -e "$$item" ] || continue; \
				name=$$(basename "$$item"); \
				target="$(TARGET_DIR)/$$dir/$$name"; \
				if [ -L "$$target" ]; then \
					echo "  [skip] $$dir/$$name (already linked)"; \
				elif [ -e "$$target" ]; then \
					echo "  [WARN] $$dir/$$name exists (not overwriting)"; \
				else \
					ln -s "$$item" "$$target"; \
					echo "  [link] $$dir/$$name"; \
				fi \
			done \
		fi \
	done
	@# Symlink individual files
	@for file in $(FILES); do \
		if [ -e "$(SOURCE_DIR)/$$file" ]; then \
			target="$(TARGET_DIR)/$$file"; \
			if [ -L "$$target" ]; then \
				echo "  [skip] $$file (already linked)"; \
			elif [ -e "$$target" ]; then \
				echo "  [WARN] $$file exists (not overwriting)"; \
			else \
				ln -s "$(SOURCE_DIR)/$$file" "$$target"; \
				echo "  [link] $$file"; \
			fi \
		fi \
	done
	@echo "Done!"

dirs:
	@# Create target directories if they don't exist
	@for dir in $(DIRS); do \
		mkdir -p "$(TARGET_DIR)/$$dir"; \
	done

uninstall:
	@echo "Removing managed symlinks..."
	@for dir in $(DIRS); do \
		if [ -d "$(SOURCE_DIR)/$$dir" ]; then \
			for item in $(SOURCE_DIR)/$$dir/*; do \
				[ -e "$$item" ] || continue; \
				name=$$(basename "$$item"); \
				target="$(TARGET_DIR)/$$dir/$$name"; \
				if [ -L "$$target" ]; then \
					rm "$$target"; \
					echo "  [removed] $$dir/$$name"; \
				fi \
			done \
		fi \
	done
	@for file in $(FILES); do \
		target="$(TARGET_DIR)/$$file"; \
		if [ -L "$$target" ]; then \
			rm "$$target"; \
			echo "  [removed] $$file"; \
		fi \
	done
	@echo "Done! Third-party items preserved."

status:
	@echo "=== Managed (symlinked to this repo) ==="
	@for dir in $(DIRS); do \
		if [ -d "$(TARGET_DIR)/$$dir" ]; then \
			for item in $(TARGET_DIR)/$$dir/*; do \
				[ -e "$$item" ] || [ -L "$$item" ] || continue; \
				if [ -L "$$item" ] && readlink "$$item" | grep -q "$(SOURCE_DIR)"; then \
					echo "  ✓ $$dir/$$(basename $$item)"; \
				fi \
			done \
		fi \
	done
	@for file in $(FILES); do \
		target="$(TARGET_DIR)/$$file"; \
		if [ -L "$$target" ] && readlink "$$target" | grep -q "$(SOURCE_DIR)"; then \
			echo "  ✓ $$file"; \
		fi \
	done
	@echo ""
	@echo "=== Third-party (not managed) ==="
	@for dir in $(DIRS); do \
		if [ -d "$(TARGET_DIR)/$$dir" ]; then \
			for item in $(TARGET_DIR)/$$dir/*; do \
				[ -e "$$item" ] || [ -L "$$item" ] || continue; \
				if [ ! -L "$$item" ] || ! readlink "$$item" | grep -q "$(SOURCE_DIR)"; then \
					echo "  • $$dir/$$(basename $$item)"; \
				fi \
			done \
		fi \
	done

clean: uninstall
	@echo "Clean complete."

# Remove dangling symlinks in the managed dirs that point into this repo.
# Use after content moves out of a managed dir (e.g. the loop skills moving
# into plugins/dev-jawn), which leaves broken links make uninstall cannot see.
prune:
	@echo "Pruning dangling symlinks that point into this repo..."
	@for dir in $(DIRS); do \
		if [ -d "$(TARGET_DIR)/$$dir" ]; then \
			for item in "$(TARGET_DIR)/$$dir"/*; do \
				[ -L "$$item" ] || continue; \
				if readlink "$$item" | grep -q "$(SOURCE_DIR)" && [ ! -e "$$item" ]; then \
					rm "$$item"; \
					echo "  [pruned] $$dir/$$(basename $$item)"; \
				fi \
			done \
		fi \
	done
	@for file in $(FILES); do \
		target="$(TARGET_DIR)/$$file"; \
		if [ -L "$$target" ] && readlink "$$target" | grep -q "$(SOURCE_DIR)" && [ ! -e "$$target" ]; then \
			rm "$$target"; \
			echo "  [pruned] $$file"; \
		fi \
	done
	@echo "Done."
