### 구글 드라이브 라이브러리(libgdrive - flaskfarm 용)
구글드라이브 API를 이용한 라이브러리 유형의 플러그인으로 구글드라이브 내 파일검색/삭제/이동/폴더탐색 등의 기능 제공

#### 기본 사항

[구글드라이브 API V3](https://developers.google.com/drive/api/v3/reference)를 사용하며, 서비스 계정/사용자 계정의 인증을 후 사용 가능

#### 제공 기능
##### 인증관련

  * 서비스계정 인증: 서비스 계정의 json 파일을 통해 API 사용 인증
    * 사용범위: 권한 있는 내 드라이브 및 공유드라이브 검색, 파일정보 확인, 바로가기 생성 (파일 삭제나 이동은 불가능)
  * 사용자계정 인증: 사용자 계정을 통해 API 사용 인증, 2단계 인증을 통해 토큰 생성 필요(1회)
    * 사용범위: 파일 삭제, 이동, 바로가기 삭제
  * rclone remote 인증: rclone.conf 파일에 포함된 정보로 API 사용 인증
    * 사용범위: remote의 권한을 따름 

##### 파일 및 폴더 탐색

  * 공유드라이브 내 모든 파일 검색
  * 특정 폴더 하위에 모든 파일/폴더 목록 얻기 (폴더 깊이 지정)
  * 특정 폴더의 자식(폴더/파일) 목록 얻기


##### 파일 생성/이동 및 삭
  * 바로가기 생성
  * 파일 삭제/이동

#### 사용방법 및 예제
- rclone remote를 통한 인증: auth_by_rclone_remote(remote)
```python
import libgdrive import *

# rclone remote 정보 로딩
remotes = ModuleBase.get_remotes(path='path/to/rclone/conf') # libgdrive에 설정한 경우 생략 가능
remote_name = 'gdrive' # 사용할 remote 명

if remote_name in remotes:
	my_remote = remotes[remote_name]
	service = LibGdrive.auth_by_rclone_remote(my_remote) # service objece를 얻어오면 GDrive API를 사용가능한 상태가된다. 
```

- 파일 정보 얻기: get_file_info(folder_id, fields=None, service=None) 
```python
#... 인증완료 service object 획득 후 ...
file_id = 'X902lkadf-sdfjklasdfaslkdfja-'

ret = LibGdrive.get_file_info(file_id, service=service)
if ret['ret'] == 'success':
    d = ret['data']
    # 파일ID, 이름, mimeType, 부모폴더ID(리스트), 삭제여부(True/False)
    print('{},{},{},{},{}'.format(d['id'], d['name'], d['mimeType'], ','.join(d['parents']), str(d['trashed']))
```
 - 기본필드는: id, name, mimeType, parent, trashed, 조회하고자 하는 필드가 있는 경우 fields에 지정 
```python
    LibGdrive.get_file_info(folder_id, fields=['id','name','trashed','size',...])
```

- 자식디렉토리 목록 얻기: get_children(target_folder_id, fields=None, service=None, time_after=None) 
```python
#... 인증완료 service object 획득 후 ...
target_folder_id = 'X902lkadf-sdfjklasdfaslkdfja-'

children = LibGdrive.get_children(target_folder_id, service=service)
for child in children:
    # 파일ID, 이름, mimeType, 부모폴더ID(리스트), 삭제여부(True/False)
    print('{},{},{},{},{}'.format(child['id'], child['name'], child['mimeType'], ','.join(child['parents']), str(child['trashed']))
```
    - time_after값(datetime)을 지정하면 지정시각 이후로 갱신된 목록만 조회

 - 파일/폴더명 변경: rename(target_fileid, new_filename, service=None) 
```python
#... 인증완료 service object 획득 후 ...
target_fileid = 'X902lkadf-sdfjklasdfaslkdfja-' #파일명을 바꿀 대상 파일/폴더ID
new_filename = '새로운 파일명'

ret = LibGdrive.rename(target_fileid, new_filename, service=service)
if ret == 'success':
    print('{},{}'.format(ret['data']['fileid'], ret['data']['name'])) # 성공시 ret['data'] 에 fileId와 변경된 파일명을 리턴

```
  - 바로가기 만들기: create_shorcut(shortcut_name, target_folder_id, parent_folder_id, service=None) 
```python
#... 인증완료 service object 획득 후 ...
shorcut_name = '바로가기 이름'
target_folder_id = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # 바로가기의 대상이 되는 파일/폴더의 ID 
parent_folder_id = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY' # 바로가기를 생성할 위치(부모폴더)의 ID

ret = LibGDrive.create_shorcut(shortcut_name, target_folder_id, parent_id, service=service)
if ret['ret'] == 'success':
    print(ret['data']['id']) # 생성된 바로가기의 ID
    print(ret['data']['shortcutDetails']) # 생성된 바로가기 새부 정보: targetId, targetMimeType
```
- Gdrive 변경사항 가져오기: get_changes_by_remote(remote, page_token=None, fields=None): 
    * remote에 drive_id가 지정되어 있는 경우 해당 drive에 대한 변경사항 감지


```python
# 30초에 한번씩 구글드라이브 변경사항 얻오오기 
remotes = ModuleBase.get_remotes(path='path/to/rclone/conf') # libgdrive에 설정한 경우 생략 가능
remote_name = 'gdrive' # 사용할 remote 명
if remote_name in remotes: remote = remotes[remote_name]
page_token = None
for i in range(10):
    # 최초 요청시 page_token을 None으로 보내면 변경사항 가져올때 사용할 start_token 값을 return
    ret = LibGdrive.get_changes_by_remote(remote, page_token=page_token)
    # 이후에는 새로운 token 으로 요청하면 해당 토큰 시점 이후 변동된 사항을 가져옴
    page_token = ret['data']['newStartPageToken']
    log(json.dumps(ret['data'], indent=2))
    time.sleep(30)
```

- 파일 복사 하기: def copy_file(cls, file_id, name, new_parent_id, service=None): 
    * 구드내 파일을 복사 지정된 폴더에 복사

```python
#... 인증완료 service object 획득 후 ...
new_filename = '새로운파일명'
file_id = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # 복사할 원본 파일 ID
parent_folder_id = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY' # 파일을 복사할 대상폴더의 ID

ret = LibGDrive.copy_file(file_id, new_filename, parent_id, service=service)
...
```
