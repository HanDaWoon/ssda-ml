# ML
## 전체 pipeline
1. 사용자의 손글씨와 함께 입력이 들어오면 `(/font_generation/images/{name})`
2. Backend단의 DM-Font를 GPU에 적재 후 사용자의 손글씨와 함께 Font-Image Generation
3. Font-Image(.png) to Font-Vector Image(.svg) 변환 (현재는 MultiProcessing, 각 요청별 Process는 40) `(/font_generation/png2svg/{name})`
4. 이렇게 생성된 Font-Vector Image를 이용해 최종적으로 Font Generation을 진행함.(미완성.)


## TODO-list
1. interrupt 처리.
2. 사용자 uuid를 이용한 코드 수정.
3. 정상적인 코드 동작을 확인할 수 있도록 BD 연결