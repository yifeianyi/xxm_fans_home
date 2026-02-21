#!/usr/bin/env python3
"""
网站安全性测试脚本 - DELETE操作测试

用于测试网站是否存在未授权的DELETE操作漏洞。

警告：
- 此脚本仅用于授权的安全测试
- 请勿用于未经授权的网站
- 使用前请确保获得网站所有者的明确许可

使用方法：
    python security_delete_test.py --url https://example.com/api/resource/1
    python security_delete_test.py --url https://example.com/api/resource/1 --token YOUR_TOKEN
    python security_delete_test.py --url https://example.com/api/resource/1 --username admin --password secret

作者：XXM Fans Home Security Team
版本：1.0.0
"""

import argparse
import sys
import requests
from requests.auth import HTTPBasicAuth
import json
from urllib.parse import urlparse
import time


class Colors:
    """终端颜色输出"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class SecurityDeleteTester:
    """DELETE操作安全性测试器"""

    def __init__(self, target_url, timeout=10):
        """
        初始化测试器

        Args:
            target_url: 目标URL
            timeout: 请求超时时间（秒）
        """
        self.target_url = target_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Security-Scanner/1.0 (Security Testing)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        self.results = []

    def parse_response_code(self, response):
        """
        解析响应中的业务状态码

        有些API返回HTTP 200，但响应体中包含自定义的错误码
        例如: {"msg":"请求访问：/xxm/socialMedia/5，认证失败，无法访问系统资源","code":401}

        Args:
            response: requests.Response对象

        Returns:
            tuple: (http_status_code, business_code, message)
        """
        http_code = response.status_code
        business_code = None
        message = None

        try:
            # 尝试解析JSON响应
            data = response.json()

            # 检查常见的业务状态码字段
            if 'code' in data:
                business_code = data['code']
            elif 'status' in data:
                business_code = data['status']
            elif 'errCode' in data:
                business_code = data['errCode']
            elif 'error_code' in data:
                business_code = data['error_code']

            # 提取消息
            if 'msg' in data:
                message = data['msg']
            elif 'message' in data:
                message = data['message']
            elif 'error' in data:
                message = data['error']

        except (json.JSONDecodeError, ValueError):
            # 响应不是JSON格式
            pass

        return http_code, business_code, message

    def is_success_response(self, response):
        """
        判断响应是否表示成功

        Args:
            response: requests.Response对象

        Returns:
            tuple: (is_success, reason)
        """
        http_code, business_code, message = self.parse_response_code(response)

        # 如果有业务状态码，优先使用业务状态码判断
        if business_code is not None:
            # 常见的成功业务码
            success_codes = [0, 200, '0', '200', 'success']
            # 常见的失败业务码
            error_codes = [401, 403, 500, '401', '403', '500', 'error', 'fail']

            if business_code in success_codes:
                return True, f"业务码: {business_code}"
            elif business_code in error_codes:
                return False, f"业务码: {business_code} - {message or '认证失败'}"

        # 如果没有业务状态码，使用HTTP状态码判断
        if http_code in [200, 201, 202, 204]:
            return True, f"HTTP状态码: {http_code}"
        elif http_code in [401, 403]:
            return False, f"HTTP状态码: {http_code} - 认证失败"

        # 默认情况下，认为不是成功响应
        return False, f"HTTP状态码: {http_code}"

    def print_banner(self):
        """打印横幅"""
        print(f"""
{Colors.CYAN}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║         网站安全性测试 - DELETE操作漏洞检测                ║
║              Website Security Testing Tool                 ║
╚════════════════════════════════════════════════════════════╝
{Colors.RESET}
        """)

    def print_result(self, test_name, status, message, details=None):
        """
        打印测试结果

        Args:
            test_name: 测试名称
            status: 状态 (PASS/FAIL/WARNING/INFO)
            message: 消息
            details: 详细信息
        """
        status_colors = {
            'PASS': Colors.GREEN,
            'FAIL': Colors.RED,
            'WARNING': Colors.YELLOW,
            'INFO': Colors.BLUE,
        }

        color = status_colors.get(status, Colors.WHITE)
        print(f"{color}{Colors.BOLD}[{status}]{Colors.RESET} {test_name}: {message}")

        if details:
            print(f"  {Colors.CYAN}详情:{Colors.RESET} {details}")

        self.results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details
        })

    def test_unauthorized_delete(self):
        """测试1：未授权DELETE操作"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试1：未授权DELETE操作{Colors.RESET}")
        print("-" * 60)

        try:
            response = self.session.delete(
                self.target_url,
                timeout=self.timeout,
                allow_redirects=False
            )

            # 解析响应
            http_code, business_code, message = self.parse_response_code(response)
            is_success, reason = self.is_success_response(response)

            # 显示响应详情
            print(f"  {Colors.CYAN}HTTP状态码:{Colors.RESET} {http_code}")
            if business_code is not None:
                print(f"  {Colors.CYAN}业务状态码:{Colors.RESET} {business_code}")
            if message:
                print(f"  {Colors.CYAN}响应消息:{Colors.RESET} {message}")

            # 判断结果
            if is_success:
                self.print_result(
                    "未授权DELETE",
                    "FAIL",
                    f"严重漏洞：未授权的DELETE操作成功！",
                    f"{reason} - 可能允许删除资源"
                )
            else:
                # 检查是否是正确的认证失败
                if business_code in [401, 403] or http_code in [401, 403]:
                    self.print_result(
                        "未授权DELETE",
                        "PASS",
                        "正确拒绝未授权访问",
                        f"{reason}"
                    )
                elif http_code == 404:
                    self.print_result(
                        "未授权DELETE",
                        "INFO",
                        "资源不存在",
                        f"{reason}"
                    )
                else:
                    self.print_result(
                        "未授权DELETE",
                        "WARNING",
                        f"未预期的响应",
                        f"{reason}"
                    )

        except requests.exceptions.Timeout:
            self.print_result(
                "未授权DELETE",
                "WARNING",
                "请求超时",
                f"超时时间: {self.timeout}秒"
            )
        except requests.exceptions.RequestException as e:
            self.print_result(
                "未授权DELETE",
                "WARNING",
                "请求失败",
                str(e)
            )


    def test_delete_with_invalid_token(self):
        """测试2：使用无效Token的DELETE操作"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试2：使用无效Token的DELETE操作{Colors.RESET}")
        print("-" * 60)

        # 设置无效的Authorization头
        headers = self.session.headers.copy()
        headers['Authorization'] = 'Bearer invalid_token_12345'

        try:
            response = requests.delete(
                self.target_url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=False
            )

            # 解析响应
            http_code, business_code, message = self.parse_response_code(response)
            is_success, reason = self.is_success_response(response)

            # 显示响应详情
            print(f"  {Colors.CYAN}HTTP状态码:{Colors.RESET} {http_code}")
            if business_code is not None:
                print(f"  {Colors.CYAN}业务状态码:{Colors.RESET} {business_code}")
            if message:
                print(f"  {Colors.CYAN}响应消息:{Colors.RESET} {message}")

            # 判断结果
            if is_success:
                self.print_result(
                    "无效Token DELETE",
                    "FAIL",
                    "严重漏洞：无效Token也能删除资源！",
                    f"{reason}"
                )
            else:
                # 检查是否是正确的认证失败
                if business_code in [401, 403] or http_code in [401, 403]:
                    self.print_result(
                        "无效Token DELETE",
                        "PASS",
                        "正确拒绝无效Token",
                        f"{reason}"
                    )
                else:
                    self.print_result(
                        "无效Token DELETE",
                        "WARNING",
                        f"未预期的响应",
                        f"{reason}"
                    )

        except requests.exceptions.RequestException as e:
            self.print_result(
                "无效Token DELETE",
                "WARNING",
                "请求失败",
                str(e)
            )

    def test_delete_with_invalid_method_override(self):
        """测试3：方法覆盖攻击（X-HTTP-Method-Override）"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试3：方法覆盖攻击{Colors.RESET}")
        print("-" * 60)

        # 尝试使用POST请求覆盖为DELETE
        headers = self.session.headers.copy()
        headers['X-HTTP-Method-Override'] = 'DELETE'

        try:
            response = requests.post(
                self.target_url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=False
            )

            # 解析响应
            http_code, business_code, message = self.parse_response_code(response)
            is_success, reason = self.is_success_response(response)

            # 显示响应详情
            print(f"  {Colors.CYAN}HTTP状态码:{Colors.RESET} {http_code}")
            if business_code is not None:
                print(f"  {Colors.CYAN}业务状态码:{Colors.RESET} {business_code}")
            if message:
                print(f"  {Colors.CYAN}响应消息:{Colors.RESET} {message}")

            # 判断结果
            if is_success:
                self.print_result(
                    "方法覆盖攻击",
                    "FAIL",
                    "严重漏洞：方法覆盖攻击成功！",
                    f"{reason} - 可能通过POST删除资源"
                )
            else:
                # 检查是否是正确的拒绝
                if business_code in [401, 403, 405] or http_code in [401, 403, 405]:
                    self.print_result(
                        "方法覆盖攻击",
                        "PASS",
                        "正确拒绝方法覆盖攻击",
                        f"{reason}"
                    )
                else:
                    self.print_result(
                        "方法覆盖攻击",
                        "WARNING",
                        f"未预期的响应",
                        f"{reason}"
                    )

        except requests.exceptions.RequestException as e:
            self.print_result(
                "方法覆盖攻击",
                "WARNING",
                "请求失败",
                str(e)
            )

    def test_delete_with_idor(self):
        """测试4：不安全的直接对象引用（IDOR）"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试4：不安全的直接对象引用（IDOR）{Colors.RESET}")
        print("-" * 60)

        # 尝试修改URL中的ID，测试是否可以删除其他用户的资源
        parsed_url = urlparse(self.target_url)
        path = parsed_url.path

        # 尝试不同的ID
        test_ids = ['1', '2', '999', 'admin', 'user']

        for test_id in test_ids:
            # 替换URL中的ID
            test_path = path.rsplit('/', 1)[0] + '/' + test_id
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{test_path}"

            try:
                response = self.session.delete(
                    test_url,
                    timeout=self.timeout,
                    allow_redirects=False
                )

                # 解析响应
                http_code, business_code, message = self.parse_response_code(response)
                is_success, reason = self.is_success_response(response)

                # 判断结果
                if is_success:
                    self.print_result(
                        f"IDOR测试 (ID={test_id})",
                        "FAIL",
                        f"严重漏洞：可能删除ID为{test_id}的资源！",
                        f"{reason}"
                    )
                    break  # 发现漏洞，停止测试
                elif business_code in [401, 403, 404] or http_code in [401, 403, 404]:
                    self.print_result(
                        f"IDOR测试 (ID={test_id})",
                        "PASS",
                        "正确拒绝访问",
                        f"{reason}"
                    )

            except requests.exceptions.RequestException as e:
                self.print_result(
                    f"IDOR测试 (ID={test_id})",
                    "WARNING",
                    "请求失败",
                    str(e)
                )

    def test_delete_with_sql_injection(self):
        """测试5：SQL注入攻击"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试5：SQL注入攻击{Colors.RESET}")
        print("-" * 60)

        # SQL注入payload
        payloads = [
            "1' OR '1'='1",
            "1; DROP TABLE users--",
            "1' UNION SELECT NULL,NULL,NULL--",
            "1' AND 1=1--",
            "1' AND 1=2--",
        ]

        parsed_url = urlparse(self.target_url)
        path = parsed_url.path

        for payload in payloads:
            # 替换URL中的ID为payload
            test_path = path.rsplit('/', 1)[0] + '/' + payload
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{test_path}"

            try:
                response = self.session.delete(
                    test_url,
                    timeout=self.timeout,
                    allow_redirects=False
                )

                if response.status_code in [200, 204, 500]:
                    self.print_result(
                        f"SQL注入测试 (payload={payload[:20]}...)",
                        "WARNING",
                        "可能存在SQL注入漏洞",
                        f"状态码: {response.status_code}"
                    )
                elif response.status_code in [400, 404]:
                    self.print_result(
                        f"SQL注入测试 (payload={payload[:20]}...)",
                        "PASS",
                        "正确拒绝恶意请求",
                        f"状态码: {response.status_code}"
                    )

            except requests.exceptions.RequestException as e:
                self.print_result(
                    f"SQL注入测试 (payload={payload[:20]}...)",
                    "WARNING",
                    "请求失败",
                    str(e)
                )

    def test_delete_with_csrf(self):
        """测试6：CSRF攻击"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试6：CSRF保护测试{Colors.RESET}")
        print("-" * 60)

        # 检查响应头中是否有CSRF保护
        try:
            response = self.session.get(
                self.target_url,
                timeout=self.timeout,
                allow_redirects=False
            )

            csrf_token = response.cookies.get('csrftoken')
            csrf_header = response.headers.get('X-CSRF-Token')

            if csrf_token or csrf_header:
                self.print_result(
                    "CSRF保护",
                    "PASS",
                    "检测到CSRF保护机制",
                    f"Cookie: {csrf_token}, Header: {csrf_header}"
                )
            else:
                self.print_result(
                    "CSRF保护",
                    "WARNING",
                    "未检测到CSRF保护机制",
                    "建议启用CSRF保护"
                )

        except requests.exceptions.RequestException as e:
            self.print_result(
                "CSRF保护",
                "WARNING",
                "请求失败",
                str(e)
            )

    def test_delete_rate_limiting(self):
        """测试7：速率限制"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试7：速率限制测试{Colors.RESET}")
        print("-" * 60)

        # 发送多个DELETE请求
        success_count = 0
        rate_limited = False

        for i in range(10):
            try:
                response = self.session.delete(
                    self.target_url,
                    timeout=self.timeout,
                    allow_redirects=False
                )

                # 解析响应
                http_code, business_code, message = self.parse_response_code(response)
                is_success, reason = self.is_success_response(response)

                if http_code == 429 or business_code == 429:
                    rate_limited = True
                    self.print_result(
                        "速率限制",
                        "PASS",
                        "检测到速率限制",
                        f"在第{i+1}次请求时触发限制"
                    )
                    break
                elif is_success:
                    success_count += 1

            except requests.exceptions.RequestException:
                pass

            time.sleep(0.1)  # 短暂延迟

        if not rate_limited and success_count > 5:
            self.print_result(
                "速率限制",
                "WARNING",
                "未检测到速率限制",
                f"成功发送{success_count}次请求"
            )

    def test_delete_with_cors(self):
        """测试8：CORS配置"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}测试8：CORS配置测试{Colors.RESET}")
        print("-" * 60)

        # 测试跨域DELETE请求
        headers = self.session.headers.copy()
        headers['Origin'] = 'http://evil.com'

        try:
            response = requests.delete(
                self.target_url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=False
            )

            cors_header = response.headers.get('Access-Control-Allow-Origin')

            if cors_header:
                if cors_header == '*':
                    self.print_result(
                        "CORS配置",
                        "WARNING",
                        "CORS配置过于宽松",
                        f"允许所有来源: {cors_header}"
                    )
                elif cors_header == 'http://evil.com':
                    self.print_result(
                        "CORS配置",
                        "FAIL",
                        "严重漏洞：允许恶意来源的跨域请求！",
                        f"允许来源: {cors_header}"
                    )
                else:
                    self.print_result(
                        "CORS配置",
                        "PASS",
                        "CORS配置合理",
                        f"允许来源: {cors_header}"
                    )
            else:
                self.print_result(
                    "CORS配置",
                    "PASS",
                    "未配置CORS或配置正确",
                    "未返回CORS头"
                )

        except requests.exceptions.RequestException as e:
            self.print_result(
                "CORS配置",
                "WARNING",
                "请求失败",
                str(e)
            )

    def print_summary(self):
        """打印测试摘要"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}═══════════════════════════════════════════════════════════════{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}测试摘要{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}═══════════════════════════════════════════════════════════════{Colors.RESET}\n")

        pass_count = sum(1 for r in self.results if r['status'] == 'PASS')
        fail_count = sum(1 for r in self.results if r['status'] == 'FAIL')
        warning_count = sum(1 for r in self.results if r['status'] == 'WARNING')
        info_count = sum(1 for r in self.results if r['status'] == 'INFO')

        print(f"{Colors.GREEN}✓ 通过: {pass_count}{Colors.RESET}")
        print(f"{Colors.RED}✗ 失败: {fail_count}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠ 警告: {warning_count}{Colors.RESET}")
        print(f"{Colors.BLUE}ℹ 信息: {info_count}{Colors.RESET}")
        print(f"{Colors.WHITE}总计: {len(self.results)}{Colors.RESET}\n")

        if fail_count > 0:
            print(f"{Colors.RED}{Colors.BOLD}发现严重漏洞！建议立即修复。{Colors.RESET}")
        elif warning_count > 0:
            print(f"{Colors.YELLOW}{Colors.BOLD}发现潜在问题，建议进一步检查。{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}未发现严重漏洞，安全性良好。{Colors.RESET}")

    def run_all_tests(self):
        """运行所有测试"""
        self.print_banner()
        print(f"{Colors.CYAN}目标URL: {self.target_url}{Colors.RESET}")
        print(f"{Colors.CYAN}开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        print(f"{Colors.CYAN}警告: 此脚本仅用于授权的安全测试{Colors.RESET}\n")

        # 运行所有测试
        self.test_unauthorized_delete()
        self.test_delete_with_invalid_token()
        self.test_delete_with_invalid_method_override()
        self.test_delete_with_idor()
        self.test_delete_with_sql_injection()
        self.test_delete_with_csrf()
        self.test_delete_rate_limiting()
        self.test_delete_with_cors()

        # 打印摘要
        self.print_summary()

        print(f"\n{Colors.CYAN}结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='网站安全性测试 - DELETE操作漏洞检测',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本测试
  python security_delete_test.py --url https://example.com/api/resource/1

  # 使用Token认证测试
  python security_delete_test.py --url https://example.com/api/resource/1 --token YOUR_TOKEN

  # 使用Basic Auth测试
  python security_delete_test.py --url https://example.com/api/resource/1 --username admin --password secret

  # 自定义超时时间
  python security_delete_test.py --url https://example.com/api/resource/1 --timeout 30

注意事项:
  - 此脚本仅用于授权的安全测试
  - 请勿用于未经授权的网站
  - 使用前请确保获得网站所有者的明确许可
  - 测试可能会对目标网站产生影响，请谨慎使用
        """
    )

    parser.add_argument(
        '--url',
        required=True,
        help='目标URL（包含资源ID）'
    )

    parser.add_argument(
        '--token',
        help='认证Token（Bearer Token）'
    )

    parser.add_argument(
        '--username',
        help='Basic Auth用户名'
    )

    parser.add_argument(
        '--password',
        help='Basic Auth密码'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='请求超时时间（秒），默认10秒'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细输出'
    )

    args = parser.parse_args()

    # 验证URL
    if not args.url.startswith(('http://', 'https://')):
        print(f"{Colors.RED}错误: URL必须以http://或https://开头{Colors.RESET}")
        sys.exit(1)

    # 创建测试器
    tester = SecurityDeleteTester(args.url, args.timeout)

    # 设置认证
    if args.token:
        tester.session.headers['Authorization'] = f'Bearer {args.token}'
        print(f"{Colors.CYAN}使用Token认证{Colors.RESET}")
    elif args.username and args.password:
        tester.session.auth = HTTPBasicAuth(args.username, args.password)
        print(f"{Colors.CYAN}使用Basic Auth认证{Colors.RESET}")

    # 运行测试
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}错误: {str(e)}{Colors.RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()