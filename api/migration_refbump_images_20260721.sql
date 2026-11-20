UPDATE company_panels
SET image_url = substr(image_url,1,instr(image_url,'10koma-shukatsu@')+15) || 'b679dad94bec476e2a726929a049f2c84e140a69' || substr(image_url, instr(image_url,'/public/images/'))
WHERE instr(image_url,'hikkoshimarche/10koma-shukatsu@') > 0 AND instr(image_url,'/public/images/') > 0;

UPDATE companies
SET thumbnail_url = substr(thumbnail_url,1,instr(thumbnail_url,'10koma-shukatsu@')+15) || 'b679dad94bec476e2a726929a049f2c84e140a69' || substr(thumbnail_url, instr(thumbnail_url,'/public/images/'))
WHERE instr(thumbnail_url,'hikkoshimarche/10koma-shukatsu@') > 0 AND instr(thumbnail_url,'/public/images/') > 0;
