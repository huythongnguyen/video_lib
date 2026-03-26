"""Resona TTS voice configuration."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


@dataclass
class VoiceConfig:
    """Configuration for a Resona TTS voice."""
    voice_id: str
    name: str
    gender: str  # "Nam" (Male) or "Nữ" (Female)
    region: str  # "Miền Bắc" (Northern) or "Miền Nam" (Southern)
    recommended_for_buddhist: bool = False
    description: Optional[str] = None


class ResonaVoice(Enum):
    """Enum of available Resona TTS voices.

    All voices are high quality. Recommended voices for Buddhist/calm content
    are marked with recommended_for_buddhist=True.

    Source: https://resona.live/vi/voices
    """

    # ==========================================
    # RECOMMENDED FOR BUDDHIST/CALM CONTENT
    # ==========================================

    THANH_NHA = VoiceConfig(
        voice_id="ES9XihN1RcFVpypacTTh",
        name="Thanh Nhã",
        gender="Nữ",
        region="Miền Bắc",
        recommended_for_buddhist=True,
        description="Elegant, calm female voice from Northern Vietnam"
    )

    TUE_AN = VoiceConfig(
        voice_id="0phiCO46biYtwYYP0DIR",
        name="Tuệ An",
        gender="Nữ",
        region="Miền Nam",
        recommended_for_buddhist=True,
        description="Wisdom and peace female voice from Southern Vietnam"
    )

    VAN_ANH = VoiceConfig(
        voice_id="ODDT6PXH9Eb43SpMXZda",
        name="Vân Anh",
        gender="Nữ",
        region="Miền Bắc",
        recommended_for_buddhist=True,
        description="Cloud reflection female voice from Northern Vietnam (DEFAULT)"
    )

    THUY_NGUYEN = VoiceConfig(
        voice_id="CBeyUXIIbS2pfymElCps",
        name="Thuỷ Nguyên",
        gender="Nữ",
        region="Miền Bắc",
        recommended_for_buddhist=True,
        description="Water source female voice from Northern Vietnam"
    )

    SUOI_CHAM_CHAP = VoiceConfig(
        voice_id="gRtmTcLs6zegO7JihCbL",
        name="Suối Chậm Chạp",
        gender="Nữ",
        region="Miền Nam",
        recommended_for_buddhist=True,
        description="Slow stream female voice from Southern Vietnam"
    )

    # ==========================================
    # OTHER AVAILABLE VOICES
    # ==========================================

    # Male Voices
    NGO_KHONG = VoiceConfig(
        voice_id="Hw8RCKYahvuS5uT8Z4Ye",
        name="Ngộ Không",
        gender="Nam",
        region="Miền Bắc"
    )

    BAT_GIOI = VoiceConfig(
        voice_id="R1CqN2exQZPOvXdMYFnq",
        name="Bát Giới",
        gender="Nam",
        region="Miền Bắc"
    )

    TRUNG_KIEN = VoiceConfig(
        voice_id="qRMFIUAS0vaFeZI5abu8",
        name="Trung Kiên",
        gender="Nam",
        region="Miền Bắc"
    )

    VIET_TRUNG = VoiceConfig(
        voice_id="GmlanOjlAHIuPeJ86ipB",
        name="Việt Trung",
        gender="Nam",
        region="Miền Bắc"
    )

    MINH_TUAN = VoiceConfig(
        voice_id="KPQJS4asbzfvJwN9fEsb",
        name="Minh Tuấn",
        gender="Nam",
        region="Miền Bắc"
    )

    HO_CUNG_RAN = VoiceConfig(
        voice_id="tak3IN3asjyDvk2dC3iR",
        name="Hổ Cứng Rắn",
        gender="Nam",
        region="Miền Bắc"
    )

    TIEN_NHANH_NHEN = VoiceConfig(
        voice_id="USYTYBI33ONlIoLQwm6d",
        name="Tiền Nhanh Nhẹn",
        gender="Nam",
        region="Miền Bắc"
    )

    HO_MIN_MANG = VoiceConfig(
        voice_id="dwK3JbXXe2LLisf6Tfx6",
        name="Hổ Mịn Màng",
        gender="Nam",
        region="Miền Bắc"
    )

    NUI_CAM_CHAY = VoiceConfig(
        voice_id="KZxq3ccG4XmAVq9ExnJE",
        name="Núi Cam Cháy",
        gender="Nam",
        region="Miền Nam"
    )

    HIEP_THUC = VoiceConfig(
        voice_id="QCWGCSBcDBqmvoWXuvCW",
        name="Hiệp Thức",
        gender="Nam",
        region="Miền Bắc"
    )

    BAO_TOI_DEN = VoiceConfig(
        voice_id="KYaeDi6NjskLfXfT5P1r",
        name="Bão Tối Đen",
        gender="Nam",
        region="Miền Bắc"
    )

    KE_LANH_BUOT = VoiceConfig(
        voice_id="DZeZtsmjaG0rWIbQ6B8V",
        name="Kệ Lạnh Buốt",
        gender="Nam",
        region="Miền Bắc"
    )

    TROI_TO_LON = VoiceConfig(
        voice_id="r3yLcbkngGdZdT2hE4Va",
        name="Trời To Lớn",
        gender="Nam",
        region="Miền Bắc"
    )

    GIAY_TOI_DEN = VoiceConfig(
        voice_id="JY46W80vwCMm3nf6ez4q",
        name="Giấy Tối Đen",
        gender="Nam",
        region="Miền Bắc"
    )

    SACH_VANG_ONG = VoiceConfig(
        voice_id="NKsNW8ppA9lzNlLjdXaJ",
        name="Sách Vàng Óng",
        gender="Nam",
        region="Miền Bắc"
    )

    SAN_KHON_NGOAN = VoiceConfig(
        voice_id="Ql3fzSgaRnot6aSfYnAh",
        name="Sàn Khôn Ngoan",
        gender="Nam",
        region="Miền Bắc"
    )

    TRAN_XUAT_SAC = VoiceConfig(
        voice_id="Wg7u9eoTOJf0b4996smf",
        name="Trần Xuất Sắc",
        gender="Nam",
        region="Miền Bắc"
    )

    GIO_HANH_PHUC = VoiceConfig(
        voice_id="3KE0nSREA3z8pB2fj7YD",
        name="Giò Hạnh Phúc",
        gender="Nam",
        region="Miền Bắc"
    )

    CAY_KHON_NGOAN = VoiceConfig(
        voice_id="JE9f7AhmbmI347tVXEtc",
        name="Cây Khôn Ngoan",
        gender="Nam",
        region="Miền Nam"
    )

    BAN_NGAN_GON = VoiceConfig(
        voice_id="2oHQU9InI5ndjhOMQPOM",
        name="Bàn Ngắn Gọn",
        gender="Nam",
        region="Miền Nam"
    )

    GIAY_HAY_HO = VoiceConfig(
        voice_id="C98DukJu88lWXoMkxndM",
        name="Giày Hay Ho",
        gender="Nam",
        region="Miền Bắc"
    )

    TUYET_HEP_HOI = VoiceConfig(
        voice_id="YnhPX6VhjR5w9ziWQ7bB",
        name="Tuyết Hẹp Hòi",
        gender="Nam",
        region="Miền Bắc"
    )

    TRA_QUY_PHAI = VoiceConfig(
        voice_id="DU6CsX1T7dMQj28Z9lnp",
        name="Trà Quý Phái",
        gender="Nam",
        region="Miền Bắc"
    )

    HEO_TOI_DEN = VoiceConfig(
        voice_id="0sGlBW3tXu3ePvf2rP7L",
        name="Heo Tối Đen",
        gender="Nam",
        region="Miền Nam"
    )

    TUYET_NHE_NHANG = VoiceConfig(
        voice_id="C3tEh3RaFrM9GXzy3lGJ",
        name="Tuyết Nhẹ Nhàng",
        gender="Nam",
        region="Miền Bắc"
    )

    NUOC_NONG_BONG = VoiceConfig(
        voice_id="nVUYb9R86xapPz0stjTw",
        name="Nước Nóng Bỏng",
        gender="Nam",
        region="Miền Nam"
    )

    BUN_DAC_BIET = VoiceConfig(
        voice_id="IheQnRUN5p6gVveNaPkv",
        name="Bún Đặc Biệt",
        gender="Nam",
        region="Miền Bắc"
    )

    # Female Voices
    MAI_THUONG = VoiceConfig(
        voice_id="uoPJ9UARkvMsZ8x0Zoaj",
        name="Mai Thương",
        gender="Nữ",
        region="Miền Bắc"
    )

    ONG_AM_AP = VoiceConfig(
        voice_id="W6vqCkz7l7n0GxNaKzyG",
        name="Ong Ấm Áp",
        gender="Nữ",
        region="Miền Bắc"
    )

    BUOM_NONG_BONG = VoiceConfig(
        voice_id="5psvYObKYOvb6zRpYUeB",
        name="Bướm Nóng Bỏng",
        gender="Nữ",
        region="Miền Bắc"
    )

    PHO_DOC_DAO = VoiceConfig(
        voice_id="HMSLcMlUWQAxu1Vd1NO4",
        name="Phở Độc Đáo",
        gender="Nữ",
        region="Miền Bắc"
    )

    GHE_NHANH_NHEN = VoiceConfig(
        voice_id="HEhDjGxPNpHaJcNjQvsH",
        name="Ghế Nhanh Nhẹn",
        gender="Nữ",
        region="Miền Bắc"
    )

    GA_XANH_LA = VoiceConfig(
        voice_id="5dNRyrnMGdbHO5ypPIPc",
        name="Gà Xanh Lá",
        gender="Nữ",
        region="Miền Bắc"
    )

    THO_CAO_RAO = VoiceConfig(
        voice_id="ygSDr73sJKhkSgERsiCB",
        name="Thỏ Cao Ráo",
        gender="Nữ",
        region="Miền Bắc"
    )

    RAN_VANG_ONG = VoiceConfig(
        voice_id="sqfAqIMRd7QvQTjYQGX3",
        name="Rắn Vàng Óng",
        gender="Nữ",
        region="Miền Bắc"
    )

    MEO_KHO_RAO = VoiceConfig(
        voice_id="d9iNLHJpr7r10IAjhvtI",
        name="Mèo Khô Ráo",
        gender="Nữ",
        region="Miền Bắc"
    )

    KINH_HONG_PHAN = VoiceConfig(
        voice_id="urTltTMVMviGIngBif76",
        name="Kính Hồng Phấn",
        gender="Nữ",
        region="Miền Bắc"
    )

    LA_HONG_PHAN = VoiceConfig(
        voice_id="PvC9LUTn1aVnx2k2ex8C",
        name="Lá Hồng Phấn",
        gender="Nữ",
        region="Miền Bắc"
    )

    MU_NON_NHO_BE = VoiceConfig(
        voice_id="EeNF9QA6WD46ytC7aPXd",
        name="Mũ Nón Nhỏ Bé",
        gender="Nữ",
        region="Miền Bắc"
    )

    MEO_MANH_ME = VoiceConfig(
        voice_id="5YOCevpLRnJNQOUFey8O",
        name="Mèo Mạnh Mẽ",
        gender="Nữ",
        region="Miền Bắc"
    )

    GIAY_THANH_TAO = VoiceConfig(
        voice_id="wlRJZJhdTgmD0LHPUeay",
        name="Giày Thanh Tao",
        gender="Nữ",
        region="Miền Bắc"
    )

    KIEN_DIU_DANG = VoiceConfig(
        voice_id="pb2N2cyodd3N8VPVPedQ",
        name="Kiến Dịu Dàng",
        gender="Nữ",
        region="Miền Bắc"
    )

    KEO_XANH_LA = VoiceConfig(
        voice_id="0Fy1bweLldClcIxNdPCw",
        name="Kẹo Xanh Lá",
        gender="Nữ",
        region="Miền Nam"
    )

    KIEN_MEM_MAI = VoiceConfig(
        voice_id="eJ89HkCfsUzbONodEne8",
        name="Kiến Mềm Mại",
        gender="Nữ",
        region="Miền Nam"
    )

    SUOI_NHANH_NHEN = VoiceConfig(
        voice_id="CngjyCLnd6wlvDjXggjq",
        name="Suối Nhanh Nhẹn",
        gender="Nữ",
        region="Miền Nam"
    )

    MEO_HAY_HO = VoiceConfig(
        voice_id="YTV4sGvY5YuVVapAwGo0",
        name="Mèo Hay Ho",
        gender="Nữ",
        region="Miền Nam"
    )

    TUI_CHAM_CHAP = VoiceConfig(
        voice_id="WKDlzjoN2GtJYxIHRIyA",
        name="Túi Chậm Chạp",
        gender="Nữ",
        region="Miền Nam"
    )

    BUT_LAP_LANH = VoiceConfig(
        voice_id="8yyyJnoFM6MMvUdo3o9R",
        name="Bút Lấp Lánh",
        gender="Nữ",
        region="Miền Bắc"
    )

    SUOI_MAT_ME = VoiceConfig(
        voice_id="ayLREiin0y8yGJD1ThxB",
        name="Suối Mát Mẻ",
        gender="Nữ",
        region="Miền Bắc"
    )

    GIUONG_NGOT_NGAO = VoiceConfig(
        voice_id="FtU7ctG0gsfoKSYznFQr",
        name="Giường Ngọt Ngào",
        gender="Nữ",
        region="Miền Nam"
    )

    @classmethod
    def get_default(cls) -> 'ResonaVoice':
        """Get default voice (Hổ Mịn Màng)."""
        return cls.HO_MIN_MANG

    @classmethod
    def get_by_name(cls, name: str) -> Optional['ResonaVoice']:
        """
        Get voice by display name or enum name (case-insensitive).

        Args:
            name: Voice display name (e.g., "Vân Anh") or enum name (e.g., "VAN_ANH", "HO_MIN_MANG")

        Returns:
            ResonaVoice enum member or None if not found
        """
        # Try enum name first (e.g., "VAN_ANH", "HO_MIN_MANG")
        try:
            return cls[name.upper()]
        except KeyError:
            pass

        # Fall back to display name matching
        name_normalized = name.lower().replace(" ", "_").replace("ă", "a").replace("â", "a").replace("ơ", "o").replace("ư", "u")
        for voice in cls:
            voice_name_normalized = voice.value.name.lower().replace(" ", "_").replace("ă", "a").replace("â", "a").replace("ơ", "o").replace("ư", "u")
            if voice_name_normalized == name_normalized:
                return voice
        return None

    @classmethod
    def get_buddhist_voices(cls) -> list['ResonaVoice']:
        """Get all voices recommended for Buddhist content."""
        return [voice for voice in cls if voice.value.recommended_for_buddhist]

    @classmethod
    def list_voices(cls, buddhist_only: bool = False) -> str:
        """
        List all available voices.

        Args:
            buddhist_only: Only show voices recommended for Buddhist content

        Returns:
            Formatted string with voice information
        """
        voices = cls.get_buddhist_voices() if buddhist_only else list(cls)

        lines = []
        if buddhist_only:
            lines.append("Recommended voices for Buddhist/calm content:")
        else:
            lines.append("All available Resona voices:")
        lines.append("")

        for voice in voices:
            config = voice.value
            marker = " (DEFAULT)" if voice == cls.VAN_ANH else ""
            lines.append(f"  {config.name}{marker}")
            lines.append(f"    Gender: {config.gender}, Region: {config.region}")
            if config.description:
                lines.append(f"    {config.description}")
            lines.append("")

        return "\n".join(lines)
