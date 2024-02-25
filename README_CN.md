# SimpleGemini


SimpleGeminiGradioApp ��һ������ʽAI����WebApp, ��ͨ��Google Gemini Pro��Gemini Pro Vision API����ʵʱ�Ի��� ֧���ı���ͼƬprompt��ʹ�����������Ҫ������������Google�����绷���� ��Ԥ����[Google AI Studio](https://makersuite.google.com/app/apikey)����API key��  

����Ŀ��[meryemsakin/GeminiGradioApp](https://github.com/meryemsakin/GeminiGradioApp)���޸İ棬��������������˱���Ի�<sup>*</sup>�Ĺ��ܡ�   

<sup>*</sup>�����¼���ᱻ�ϴ��������ڱ����û��ļ���(����C:\user\username)\.simplegemini\log�ļ��������������������ļ����У��������ֺ�ͼƬ��

�����¼�ļ�û�м��ܣ���ע����˽��ȫ�������¼�е�ͼƬ����С��������512x512���ص�Ԥ��ͼ�Խ�ʡ���̿ռ䣬���Ǿ��������ĶԻ�����Ȼ����ռ�úܶ�ռ䣬�붨ʱ����

App���½���"Save to LOG"��ѡ��Ĭ���ǹ�ѡ״̬�����ȡ����ѡ����ǰ���������¼���ᱻ���档

![image](images/simple_genini_ui.png)

### ��װ

��[�ٶ�����](https://pan.baidu.com/s/1DBilb4ZU3keQ8NG7MYhSIQ?pwd=gad9)�ṩ�����ϰ�, ���غ�ֻ��Ҫ����API-key����ʹ�á�
* �������ϰ�Ȼ���ѹ��  
* �ҵ�```SimpleGemini\apikey.json```�����ı��༭���(������±�)������ļ����ڵڶ���"GOOGLE_API_KEY": �����˫����""���������Google API key, �������ļ���
![image](images/api_key.png)
* �ҵ�```SimpleGemini\run_gemini_python_embeded.bat```��˫�����С�ע����ȷ��������绷����������ʹ��Gemini��


�ֶ����𷽷����£���װ˵�������Windows������ƽ̨�����в��ղ���

* ����ȷ�ϰ�װ��Python 3.10���ϰ汾, ������[Google AI Studio](https://makersuite.google.com/app/apikey)�����API key��

* ���նˣ������������¡����ֿ�:
```
git clone https://github.com/chflame163/SimpleGemini.git
```
* ������ĿĿ¼:
```
cd SimpleGemini
```
* ����venv:
```
python.exe -m venv venv 
```
* Ϊvenv��װ����Ŀ������:
```
.\venv\Scripts\python.exe -m pip install -r .\requirements.txt
```
* �ر��ն˴��ڡ�����Դ���������ҵ�```SimpleGemini\apikey.json```�����ı��༭���(������±�)������ļ����ڵڶ���"GOOGLE_API_KEY": �����˫����""���������Google API key, �������ļ���
![image](images/api_key.png)

* ��װ��ɣ��ҵ�```SimpleGemini\run_gemini_venv.bat```��˫�����С�ע����ȷ��������绷����������ʹ��Gemini��
