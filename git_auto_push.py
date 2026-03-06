#!/usr/bin/env python3
"""
GitHub自动推送脚本
功能：每30分钟自动拉取最新代码 → 添加修改 → 提交 → 推送到main分支
"""
import os
import subprocess
import time
import schedule

# 开发环境用本地路径，Docker内用 /app
REPO_DIR = os.environ.get("REPO_DIR", "/home/node/.openclaw/workspace/mall")
GITHUB_REPO = "https://github.com/zkk515/mall-vue-python.git"
COMMIT_MSG_PREFIX = "feat:"

def run_cmd(cmd, cwd=REPO_DIR, check=True):
    """执行shell命令"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ 命令失败: {cmd}")
            print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False

def git_pull():
    """拉取最新代码（避免冲突）"""
    print("🔄 拉取最新代码...")
    run_cmd("git fetch origin")
    run_cmd("git checkout main")
    run_cmd("git pull origin main", check=False)

def git_add_and_commit():
    """添加修改并提交"""
    print("📝 检查修改...")
    run_cmd("git status", check=False)
    
    # 添加所有修改
    run_cmd("git add -A", check=False)
    
    # 检查是否有修改
    result = subprocess.run("git diff --cached --quiet", shell=True, cwd=REPO_DIR)
    if result.returncode == 0:
        print("✅ 没有需要提交的修改")
        return False
    
    # 生成提交信息
    import datetime
    commit_msg = f"{COMMIT_MSG_PREFIX} Auto sync at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"📤 提交: {commit_msg}")
    run_cmd(f'git commit -m "{commit_msg}"', check=False)
    return True

def git_push():
    """推送到GitHub"""
    print("🚀 推送到GitHub...")
    # 设置GitHub凭据（需要提前配置token或SSH密钥）
    # run_cmd("git push origin main")
    print("⚠️  请手动配置GitHub凭据后取消注释上面的命令")

def auto_push():
    """自动推送流程"""
    print("=" * 50)
    print("🚀 开始自动推送...")
    print("=" * 50)
    
    git_pull()
    if git_add_and_commit():
        git_push()
    
    print("✅ 完成\n")

def main():
    """主函数：定时执行"""
    # 首次执行
    auto_push()
    
    # 每30分钟执行一次
    schedule.every(30).minutes.do(auto_push)
    
    print("⏰ Git自动推送服务已启动，每30分钟执行一次")
    print(f"📁 仓库目录: {REPO_DIR}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
