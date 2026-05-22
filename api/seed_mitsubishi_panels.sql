-- 三菱商事 10コマ panel データ（jsDelivr CDN版）
DELETE FROM company_panels WHERE company_id = 'mitsubishi_corp';

INSERT INTO company_panels (company_id, panel_num, image_url, character, dialogue) VALUES
('mitsubishi_corp', 1,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_01.png',
'nana',
'三菱商事って、就活でよく聞くけど…実際、何をしている会社なの？'),

('mitsubishi_corp', 2,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_02.png',
'haruki',
'一言でいうと、世界規模で事業をつくる総合商社。2026年3月期の収益は18兆9,160億円だよ。'),

('mitsubishi_corp', 3,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_03.png',
'nana',
'商社って、モノを買って売るだけの会社だと思ってた。それだけでそんな規模になるの？'),

('mitsubishi_corp', 4,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_04.png',
'haruki',
'三菱商事は、売買だけじゃない。資源に投資し、インフラをつくり、生活消費まで関わる会社なんだ。'),

('mitsubishi_corp', 5,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_05.png',
'haruki',
'利益の柱は金属資源と地球環境エネルギー。この2つで純利益の約45.6%を占めているよ。'),

('mitsubishi_corp', 6,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_06.png',
'nana',
'でも、資源だけじゃなくて、生活にも近いんだね。ローソンや三菱食品も関係あるんだ！'),

('mitsubishi_corp', 7,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_07.png',
'nana',
'やっぱり人気企業だし、給料や働き方も気になる…。実際どうなの？'),

('mitsubishi_corp', 8,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_08.png',
'haruki',
'総合職の初任給は学部卒35万円、修士卒38.5万円。平均年収は2,033万円、残業は月31時間だよ。'),

('mitsubishi_corp', 9,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_09.png',
'nana',
'選考、やっぱり狭き門だよね？2026年度入社は何人くらい採用されたの？'),

('mitsubishi_corp', 10,
'https://cdn.jsdelivr.net/gh/hikkoshimarche/10koma-shukatsu@main/public/images/mitsubishi/panel_10.png',
'haruki',
'2026年度入社は130名。大事なのは、好奇心・挑戦・三綱領への共感だね。');