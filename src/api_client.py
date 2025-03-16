import requests
from typing import Dict, Optional, Union
from enum import Enum

class EndpointType(Enum):
    """接口类型枚举"""
    GET_ANNOUNCEMENT = 1
    GET_CORE_DATA = 2
    GET_LATEST_VERSION = 3
    GET_VMP_AUTH = 4
    GET_PURCHASE_LINK = 5
    GET_DOWNLOAD_URL = 6
    GET_VARIABLE_DATA = 7
    CHECK_USER_STATUS = 8
    USER_REGISTER = 10
    USER_LOGIN = 11
    USER_RECHARGE = 12
    USER_CHANGE_PWD = 13
    USER_REBIND = 14
    USER_LOGOUT = 15
    TRIAL_SOFTWARE = 16
    SINGLE_CODE_LOGIN = 17
    BAN_USER = 18
    SET_USER_DATA = 19
    ADD_BLACKLIST = 20
    GET_SPECIFIC_DATA = 21
    GET_USER_DETAILS = 22
    GET_RECHARGE_INFO = 23
    GET_EXPIRY_TIME = 24
    GET_REMAINING_POINTS = 25
    DEDUCT_POINTS = 26
    GET_VERSION_DATA = 27

class ApiClient:
    """文心云WebAPI完整封装"""
    
    def __init__(self, soft_id: str, version: str, mac: str):
        self.soft_id = soft_id
        self.version = version
        self.mac = mac
        self.base_urls = [
            "http://api.1wxyun.com/",
            "http://api2.1wxyun.com/"
        ]
        self.timeout = 2
        self.error_codes = {
                            # 基础服务错误
                            "-81001": "接口不存在，请检查接口地址是否正确",
                            "-81003": "软件服务已被暂停，请联系管理员",
                            "-81004": "软件不存在，请确认软件标识是否正确",
                            "-81005": "软件已停用，请使用最新版本",
                            "-81006": "版本号不存在，请检查更新",
                            "-81007": "接口密码错误，请联系开发者",
                            "-81008": "当前软件不允许账户转移绑定",
                            "-81009": "当前为免费版本，请升级到付费版",
                            "-81010": "版本已停用，请下载最新版本",
                            "-81011": "版本号格式错误，必须为数字",
                            "-81012": "当前未开放试用功能",
                            "-81015": "操作过于频繁，请10分钟后再试",
                            "-81016": "同一IP访问次数过多，请稍后再试",
                            "-81017": "请求数据需要加密后再提交",
                            "-81018": "变量数据不存在，请检查变量编号",
                            "-81019": "变量编号必须为数字",
                            "-81020": "变量别名只能包含字母和数字",
                            "-81021": "调用方式错误，请检查请求参数",
                            "-81022": "机器码格式错误（需32位以内字母/数字）",
                            "-81023": "请先登录或账号已被强制下线",
                            "-81024": "扣除点数必须大于零",
                            "-81025": "卡类型与软件收费模式不匹配",
                            "-81026": "时间计费模式下无法使用点数扣除",
                            "-81027": "黑名单已存在该设备",
                            "-81028": "账号在其他设备登录，请10分钟后再试",
                            "-81029": "账号在异地IP登录，请10分钟后再试",
                            "-81030": "超过同时登录数量限制",
                            "-81031": "账号已在其他设备登录",
                            "-81032": "Token格式错误（需16位字母/数字）",
                            "-81033": "用户名/单码格式错误（6-16位字母/数字）",
                            "-81035": "解绑类型只能为1（机器码）或2（IP）",
                            "-81036": "用户点数不足",
                            "-81037": "当前版本已过期，请更新",
                            "-81039": "设备已被列入黑名单",
                            "-81040": "状态检测过于频繁，间隔需≥3分钟",
                            "-81042": "云端数据超过最大长度限制",
                            "-81043": "封停原因描述过长",
                            "-81044": "黑名单原因描述过长",
                            "-81045": "VMP授权密钥配置错误",
                            "-81047": "VMP机器码格式错误（10-200字符）",
                            "-81048": "VMP授权验证失败",
                            "-81049": "获取指定数据失败",
                            
                            # 单码相关错误
                            "-83001": "卡密不存在，请检查输入",
                            "-83002": "卡密格式错误（需16位字符）",
                            "-83003": "卡密已被锁定",
                            "-83004": "卡密类型与软件收费模式不符",
                            "-83005": "单次卡密每台设备只能使用一次",
                            "-83006": "卡密已过期",
                            "-83007": "卡密剩余点数不足",
                            "-83008": "未在绑定设备使用",
                            "-83009": "未在绑定IP地址使用",
                            "-83011": "卡密转绑次数超限",
                            "-83012": "卡密积分不足",
                            "-83013": "卡密未激活",
                            "-83014": "当前IP与绑定IP一致无需转绑",
                            "-83015": "当前设备与绑定设备一致无需转绑",
                            "-83016": "转绑后卡密将立即过期",
                            "-83017": "转绑后卡密点数将变为负数",
                            "-83018": "卡密不存在/已被封禁",

                            # 用户账户错误
                            "-82001": "用户不存在",
                            "-82002": "用户名格式错误（6-16位字母/数字）",
                            "-82003": "密码格式错误（6-16位字母/数字）",
                            "-82004": "超级密码格式错误",
                            "-82005": "用户名已被注册",
                            "-82006": "账户已被锁定",
                            "-82007": "账户已过期",
                            "-82008": "用户点数不足",
                            "-82009": "未在绑定设备登录",
                            "-82010": "未在绑定IP登录",
                            "-82011": "注册次数超限",
                            "-82012": "转绑次数超限",
                            "-82013": "用户积分不足",
                            "-82014": "当前IP与绑定IP一致",
                            "-82015": "当前设备与绑定设备一致",
                            "-82016": "注册功能已关闭",
                            "-82017": "需使用卡密进行注册",
                            "-82018": "超级密码错误",
                            "-82019": "转绑后账户将立即过期",
                            "-82020": "转绑后账户点数将变为负数",
                            "-82021": "用户名或密码错误",
                            "-82022": "推荐人信息格式错误",
                            "-82023": "用户数量已达上限",
                            "-82024": "账户不存在/密码错误/已被封禁",

                            # 充值相关错误
                            "-84001": "充值卡格式错误（需16位字符）",
                            "-84002": "充值卡不存在",
                            "-84003": "充值卡已被使用",
                            "-84004": "充值卡已被锁定",
                            "-84005": "单次充值卡每个用户限用一张",

                            # 试用相关错误
                            "-85001": "试用积分不足",
                            "-85002": "试用特征不存在",
                            "-85003": "试用特征已锁定",
                            "-85004": "无相关试用数据",
                            "-85005": "试用已过期",
                            "-85006": "试用点数不足",
                            "-85007": "试用特征格式错误",

                            # 系统级错误
                            "-81060": "超过最大激活用户数",
                            "-83018": "卡密/试用特征不存在或已被封禁",
                            "-82024": "账户异常，请联系客服"
                        }  # 根据文档补充错误码

    def _build_params(self, endpoint_type: EndpointType, **kwargs) -> Dict:
        params = {"Softid": self.soft_id, "type": endpoint_type.value}
        params.update({k: v for k, v in kwargs.items() if v is not None})
        return params

    def _send_request(self, params: Dict) -> Union[str, Dict]:
        """
        发送请求，严格遵循文档规范
        :param params: 请求参数字典，必须包含type参数
        :return: 响应数据或错误信息
        """
        endpoint_type = params.get("type")  # 获取接口类型
        if not endpoint_type:
            return "请求参数错误：缺少type参数"

        for url in self.base_urls:
            try:
                # 构建符合文档规范的URL
                full_url = f"{url}?type={endpoint_type}"
                # 发送POST请求，确保参数以表单形式提交
                response = requests.post(full_url, data=params, timeout=self.timeout)
                
                if response.ok:
                    response_text = response.text.strip()
                    # 判断是否为错误码
                    if response_text.startswith("-"):
                        return False, self.error_codes.get(response_text, f"未知错误码: {response_text}")
                    else:
                        return True, response_text  # 返回成功响应
            except (requests.Timeout, requests.ConnectionError) as e:
                print(f"请求失败，切换备用地址: {e}")
                continue  # 切换备用地址
        return False, "接口调用失效"

    # -------------------- 完整接口实现 --------------------
    
    def get_announcement(self) -> Union[str, Dict]:
        """1. 获取公告"""
        return self._send_request(self._build_params(EndpointType.GET_ANNOUNCEMENT))
    
    def get_core_data(self, user_name: str, token: str) -> Union[str, Dict]:
        """2. 取核心数据"""
        return self._send_request(self._build_params(
            EndpointType.GET_CORE_DATA,
            UserName=user_name,
            Token=token
        ))
    
    def get_latest_version(self) -> Union[str, Dict]:
        """3. 取最新版本号"""
        return self._send_request(self._build_params(EndpointType.GET_LATEST_VERSION))
    
    def get_vmp_authorization(self, user_name: str, token: str, vmp_mac: str) -> Union[str, Dict]:
        """4. 取VMP授权"""
        return self._send_request(self._build_params(
            EndpointType.GET_VMP_AUTH,
            UserName=user_name,
            Token=token,
            VmpMac=vmp_mac
        ))
    
    def get_purchase_link(self) -> Union[str, Dict]:
        """5. 取购卡链接"""
        return self._send_request(self._build_params(EndpointType.GET_PURCHASE_LINK))
    
    def get_download_url(self) -> Union[str, Dict]:
        """6. 取下载地址"""
        return self._send_request(self._build_params(EndpointType.GET_DOWNLOAD_URL))
    
    def get_variable_data(self, user_name: str, token: str, var_id: str, var_name: str) -> Union[str, Dict]:
        """7. 取变量数据"""
        return self._send_request(self._build_params(
            EndpointType.GET_VARIABLE_DATA,
            UserName=user_name,
            Token=token,
            VariableId=var_id,
            VariableName=var_name
        ))
    
    def check_user_status(self, user_name: str, token: str) -> Union[str, Dict]:
        """8. 检测用户状态"""
        return self._send_request(self._build_params(
            EndpointType.CHECK_USER_STATUS,
            UserName=user_name,
            Token=token
        ))
    
    def user_register(self, user_name: str, password: str, super_pwd: str, 
                     card_pwd: str, recommender: str = None) -> Union[str, Dict]:
        """10. 用户注册"""
        return self._send_request(self._build_params(
            EndpointType.USER_REGISTER,
            UserName=user_name,
            UserPwd=password,
            SupPwd=super_pwd,
            CardPwd=card_pwd,
            Mac=self.mac,
            Recommender=recommender
        ))
    
    def user_login(self, user_name: str, password: str) -> Union[str, Dict]:
        """11. 用户登录"""
        return self._send_request(self._build_params(
            EndpointType.USER_LOGIN,
            UserName=user_name,
            UserPwd=password,
            Version=self.version,
            Mac=self.mac
        ))
    
    def user_recharge(self, user_name: str, card_pwd: str) -> Union[str, Dict]:
        """12. 用户充值"""
        return self._send_request(self._build_params(
            EndpointType.USER_RECHARGE,
            UserName=user_name,
            CardPwd=card_pwd
        ))
    
    def user_change_password(self, user_name: str, super_pwd: str, new_pwd: str) -> Union[str, Dict]:
        """13. 用户改密"""
        return self._send_request(self._build_params(
            EndpointType.USER_CHANGE_PWD,
            UserName=user_name,
            SupPwd=super_pwd,
            NewUserPwd=new_pwd
        ))
    
    def user_rebind(self, user_name: str, password: Optional[str], 
                   rebind_type: int, new_mac: str) -> Union[str, Dict]:
        """14. 用户转绑"""
        return self._send_request(self._build_params(
            EndpointType.USER_REBIND,
            UserName=user_name,
            UserPwd=password,
            Type=rebind_type,
            Mac=new_mac
        ))
    
    def user_logout(self, user_name: str, token: str) -> Union[str, Dict]:
        """15. 用户退出"""
        return self._send_request(self._build_params(
            EndpointType.USER_LOGOUT,
            UserName=user_name,
            Token=token
        ))
    
    def trial_software(self, user_id: str) -> Union[str, Dict]:
        """16. 试用软件"""
        return self._send_request(self._build_params(
            EndpointType.TRIAL_SOFTWARE,
            Userid=user_id,
            Version=self.version
        ))
    
    def single_code_login(self, card: str) -> Union[str, Dict]:
        """17. 单码登录"""
        return self._send_request(self._build_params(
            EndpointType.SINGLE_CODE_LOGIN,
            Card=card,
            Version=self.version,
            Mac=self.mac
        ))
    
    def ban_user(self, user_name: str, password: Optional[str] = None) -> Union[str, Dict]:
        """18. 封停用户"""
        return self._send_request(self._build_params(
            EndpointType.BAN_USER,
            UserName=user_name,
            UserPwd=password
        ))
    
    def set_user_data(self, user_name: str, token: str, data: str) -> Union[str, Dict]:
        """19. 置用户云数据"""
        return self._send_request(self._build_params(
            EndpointType.SET_USER_DATA,
            UserName=user_name,
            Token=token,
            Data=data
        ))
    
    def add_blacklist(self, mac: str, reason: str) -> Union[str, Dict]:
        """20. 加入黑名单"""
        return self._send_request(self._build_params(
            EndpointType.ADD_BLACKLIST,
            Mac=mac,
            Reason=reason
        ))
    
    def get_specific_data(self, user_name: str, token: str, data_type: int) -> Union[str, Dict]:
        """21. 取用户指定数据"""
        return self._send_request(self._build_params(
            EndpointType.GET_SPECIFIC_DATA,
            UserName=user_name,
            Token=token,
            Type=data_type
        ))
    
    def get_user_details(self, user_name: str, password: Optional[str] = None) -> Union[str, Dict]:
        """22. 取用户详细数据"""
        return self._send_request(self._build_params(
            EndpointType.GET_USER_DETAILS,
            UserName=user_name,
            UserPwd=password
        ))
    
    def get_recharge_info(self, user_name: str, password: Optional[str] = None) -> Union[str, Dict]:
        """23. 取用户充值信息"""
        return self._send_request(self._build_params(
            EndpointType.GET_RECHARGE_INFO,
            UserName=user_name,
            UserPwd=password
        ))
    
    def get_expiry_time(self, user_name: str, password: Optional[str] = None) -> Union[str, Dict]:
        """24. 取到期时间"""
        return self._send_request(self._build_params(
            EndpointType.GET_EXPIRY_TIME,
            UserName=user_name,
            UserPwd=password
        ))
    
    def get_remaining_points(self, user_name: str, password: Optional[str] = None) -> Union[str, Dict]:
        """25. 取剩余点数"""
        return self._send_request(self._build_params(
            EndpointType.GET_REMAINING_POINTS,
            UserName=user_name,
            UserPwd=password
        ))
    
    def deduct_points(self, user_name: str, token: str, quantity: int) -> Union[str, Dict]:
        """26. 扣除点数"""
        return self._send_request(self._build_params(
            EndpointType.DEDUCT_POINTS,
            UserName=user_name,
            Token=token,
            Quantity=quantity
        ))
    
    def get_version_data(self, user_name: str, token: str) -> Union[str, Dict]:
        """27. 取版本号数据"""
        return self._send_request(self._build_params(
            EndpointType.GET_VERSION_DATA,
            UserName=user_name,
            Token=token,
            Version=self.version
        ))
    


