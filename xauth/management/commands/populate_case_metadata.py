"""
Django management command to populate fake tags and options for cases
Usage: python manage.py populate_case_metadata
"""
import random
from django.core.management.base import BaseCommand
from xauth.models import CaseMetadata, CaseTag, CaseOption
from xauth.file_manager import FileManager


class Command(BaseCommand):
    help = '为指定 casespace 的所有 case 添加假数据（tags 和 options）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--casespace',
            type=str,
            default='casespace1',
            help='Casespace 名称 (默认: casespace1)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后重新生成'
        )

    def handle(self, *args, **options):
        casespace = options['casespace']
        clear_existing = options['clear']

        self.stdout.write(self.style.SUCCESS(f'开始为 {casespace} 生成假数据...'))

        # 初始化 FileManager
        file_manager = FileManager()

        # 获取所有 cases
        try:
            cases = file_manager.get_cases(casespace)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'获取 cases 失败: {e}'))
            return

        if not cases:
            self.stdout.write(self.style.WARNING(f'{casespace} 中没有找到任何 case'))
            return

        self.stdout.write(f'找到 {len(cases)} 个 case')

        # 预定义的假数据
        fake_tags = [
            '性能测试', '功能测试', '单元测试', '集成测试', '回归测试',
            '冒烟测试', '压力测试', 'UI测试', 'API测试', '安全测试',
            '兼容性测试', '自动化', '手动', '高优先级', '中优先级',
            '低优先级', 'Bug修复', '新功能', '优化', '重构',
            'V1.0', 'V2.0', 'Android', 'iOS', 'Web',
            '前端', '后端', '数据库', '待审核', '已完成'
        ]

        fake_option_keys = [
            'priority', 'status', 'assignee', 'version', 'platform',
            'browser', 'environment', 'duration', 'retry_count', 'timeout',
            'author', 'reviewer', 'category', 'module', 'severity'
        ]

        fake_option_values = {
            'priority': ['P0', 'P1', 'P2', 'P3', 'P4'],
            'status': ['待执行', '执行中', '已完成', '已阻塞', '已跳过'],
            'assignee': ['张三', '李四', '王五', '赵六', 'Admin'],
            'version': ['v1.0', 'v1.1', 'v2.0', 'v2.1', 'v3.0'],
            'platform': ['Windows', 'Linux', 'MacOS', 'Android', 'iOS'],
            'browser': ['Chrome', 'Firefox', 'Safari', 'Edge', 'IE11'],
            'environment': ['dev', 'test', 'staging', 'production'],
            'duration': ['1分钟', '5分钟', '10分钟', '30分钟', '1小时'],
            'retry_count': ['0', '1', '2', '3', '5'],
            'timeout': ['30s', '60s', '120s', '300s', '600s'],
            'author': ['测试团队', '开发团队', 'QA团队', '产品团队'],
            'reviewer': ['技术负责人', '项目经理', 'QA负责人'],
            'category': ['功能测试', '性能测试', '安全测试', '兼容性测试'],
            'module': ['登录模块', '支付模块', '订单模块', '用户模块', '商品模块'],
            'severity': ['致命', '严重', '一般', '轻微', '建议']
        }

        # 统计
        created_count = 0
        updated_count = 0
        tags_added = 0
        options_added = 0

        for case in cases:
            case_name = case['name']
            
            # 如果需要清除现有数据
            if clear_existing:
                CaseMetadata.objects.filter(
                    casespace=casespace,
                    case_name=case_name
                ).delete()

            # 创建或获取 CaseMetadata
            metadata, created = CaseMetadata.objects.get_or_create(
                casespace=casespace,
                case_name=case_name
            )

            if created:
                created_count += 1
                self.stdout.write(f'  创建: {case_name}')
            else:
                updated_count += 1
                self.stdout.write(f'  更新: {case_name}')

            # 添加随机数量的标签 (3-8个)
            if clear_existing or not metadata.tags.exists():
                num_tags = random.randint(3, 8)
                selected_tags = random.sample(fake_tags, num_tags)
                
                for tag in selected_tags:
                    CaseTag.objects.get_or_create(
                        metadata=metadata,
                        tag=tag
                    )
                    tags_added += 1

                self.stdout.write(f'    添加了 {num_tags} 个标签')

            # 添加随机数量的选项 (3-6个)
            if clear_existing or not metadata.options.exists():
                num_options = random.randint(3, 6)
                selected_keys = random.sample(fake_option_keys, num_options)
                
                for key in selected_keys:
                    value = random.choice(fake_option_values.get(key, ['N/A']))
                    CaseOption.objects.get_or_create(
                        metadata=metadata,
                        key=key,
                        defaults={'value': value}
                    )
                    options_added += 1

                self.stdout.write(f'    添加了 {num_options} 个选项')

        # 输出统计信息
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('数据生成完成！'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Casespace: {casespace}')
        self.stdout.write(f'总 Case 数: {len(cases)}')
        self.stdout.write(f'新创建: {created_count}')
        self.stdout.write(f'已存在: {updated_count}')
        self.stdout.write(f'总标签数: {tags_added}')
        self.stdout.write(f'总选项数: {options_added}')
        self.stdout.write(self.style.SUCCESS('='*50))

