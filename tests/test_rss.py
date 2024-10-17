from animepipeline.rss.nyaa import parse_nyaa


def test_parse_nyaa() -> None:
    # 测试解析nyaa rss
    res = parse_nyaa(
        "https://nyaa.si/?page=rss&q=%5BSubsPlease%5D+Make+Heroine+ga+Oosugiru%21+-++%281080p%29&c=0_0&f=0"
    )
    print(res)
    assert len(res) > 0
