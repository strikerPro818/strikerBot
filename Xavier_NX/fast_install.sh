#!/bin/bash

## purple to echo
function purple(){
    echo -e "\033[35m$1\033[0m"
}


## green to echo
function green(){
    echo -e "\033[32m$1\033[0m"
}

## Error to warning with blink
function bred(){
    echo -e "\033[31m\033[01m\033[05m$1\033[0m"
}

## Error to warning with blink
function byellow(){
    echo -e "\033[33m\033[01m\033[05m$1\033[0m"
}


## Error
function red(){
    echo -e "\033[31m\033[01m$1\033[0m"
}

## warning
function yellow(){
    echo -e "\033[33m\033[01m$1\033[0m"
}

path='http://paddlepaddle.org/download?url='
release_version=`curl -s https://pypi.org/project/paddlepaddle/|grep -E "/project/paddlepaddle/"|grep "release"|awk -F '/' '{print $(NF-1)}'|head -1`
python_list=(
"27"
"35"
"36"
"37"
)


function use_cpu(){
   while true
    do
     read -p "æ˜¯å¦å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddleï¼Ÿ(y/n)" cpu_option
     cpu_option=`echo $cpu_option | tr 'A-Z' 'a-z'`
     if [[ "$cpu_option" == "" || "$cpu_option" == "n" ]];then
        echo "é€€å‡ºå®‰è£…ä¸­..."
        exit
     else
        GPU='cpu'
        echo "å°†ä¸ºæ‚¨å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddle"
        break
     fi
    done
}

function checkLinuxCUDNN(){
   echo
   read -n1 -p "è¯·æŒ‰å›žè½¦é”®è¿›è¡Œä¸‹ä¸€æ­¥..."
   echo
   while true
   do
       version_file='/usr/local/cuda/include/cudnn.h'
       if [ -f "$version_file" ];then
          CUDNN=`cat $version_file | grep CUDNN_MAJOR |awk 'NR==1{print $NF}'`
       fi
       if [ "$CUDNN" == "" ];then
           version_file=`sudo find /usr -name "cudnn.h"|head -1`
           if [ "$version_file" != "" ];then
               CUDNN=`cat ${version_file} | grep CUDNN_MAJOR -A 2|awk 'NR==1{print $NF}'`
           else
               echo "æ£€æµ‹ç»“æžœï¼šæœªåœ¨å¸¸è§„è·¯å¾„ä¸‹æ‰¾åˆ°cuda/include/cudnn.hæ–‡ä»¶"
               while true
               do
                  read -p "è¯·æ ¸å®žcudnn.hä½ç½®ï¼Œå¹¶åœ¨æ­¤è¾“å…¥è·¯å¾„ï¼ˆè¯·æ³¨æ„ï¼Œè·¯å¾„éœ€è¦è¾“å…¥åˆ°â€œcudnn.hâ€è¿™ä¸€çº§ï¼‰:" cudnn_version
                  echo
                  if [ "$cudnn_version" == "" ] || [ ! -f "$cudnn_version" ];then
                        read -p "ä»æœªæ‰¾åˆ°cuDNNï¼Œè¾“å…¥yå°†å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddleï¼Œè¾“å…¥nå¯é‡æ–°å½•å…¥cuDNNè·¯å¾„ï¼Œè¯·è¾“å…¥ï¼ˆy/nï¼‰" cpu_option
                        echo
                        cpu_option=`echo $cpu_option | tr 'A-Z' 'a-z'`
                        if [ "$cpu_option" == "y" -o "$cpu_option" == "" ];then
                            GPU='cpu'
                            break
                        else
                            echo "è¯·é‡æ–°è¾“å…¥"
                            echo
                        fi
                  else
                     CUDNN=`cat $cudnn_version | grep CUDNN_MAJOR |awk 'NR==1{print $NF}'`
                     echo "æ£€æµ‹ç»“æžœï¼šæ‰¾åˆ°cudnn.h"
                     break
                  fi
                 done
             if [ "$GPU" == "cpu" ];then
                break
             fi
           fi
       fi
       if [ "$CUDA" == "9" -a "$CUDNN" != "7" ];then
           echo
           echo "ç›®å‰CUDA9ä¸‹ä»…æ”¯æŒcuDNN7ï¼Œæš‚ä¸æ”¯æŒæ‚¨æœºå™¨ä¸Šçš„CUDNN${CUDNN}ã€‚æ‚¨å¯ä»¥è®¿é—®NVIDIAå®˜ç½‘ä¸‹è½½é€‚åˆç‰ˆæœ¬çš„CUDNNï¼Œè¯·ctrl+cé€€å‡ºå®‰è£…è¿›ç¨‹ã€‚æŒ‰å›žè½¦é”®å°†ä¸ºæ‚¨å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddle"
           echo
          use_cpu()
          if [ "$GPU"=="cpu" ];then
             break
          fi
       fi

       if [ "$CUDNN" == 5 ] || [ "$CUDNN" == 7 ];then
          echo
          echo "æ‚¨çš„CUDNNç‰ˆæœ¬æ˜¯: CUDNN$CUDNN"
          break
       else
          echo
          read -n1 -p "ç›®å‰æ”¯æŒçš„CUDNNç‰ˆæœ¬ä¸º5å’Œ7,æš‚ä¸æ”¯æŒæ‚¨æœºå™¨ä¸Šçš„CUDNN${CUDNN}ï¼Œå°†ä¸ºæ‚¨å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddle,è¯·æŒ‰å›žè½¦é”®å¼€å§‹å®‰è£…"
          echo
          use_cpu
          if [ "$GPU"=="cpu" ];then
             break
          fi
       fi
   done
}

function checkLinuxCUDA(){
   while true
   do
       CUDA=`echo ${CUDA_VERSION}|awk -F "[ .]" '{print $1}'`
       if [ "$CUDA" == "" ];then
         if [ -f "/usr/local/cuda/version.txt" ];then
           CUDA=`cat /usr/local/cuda/version.txt | grep 'CUDA Version'|awk -F '[ .]' '{print $3}'`
           tmp_cuda=$CUDA
         fi
         if [ -f "/usr/local/cuda8/version.txt" ];then
           CUDA=`cat /usr/local/cuda8/version.txt | grep 'CUDA Version'|awk -F '[ .]' '{print $3}'`
           tmp_cuda8=$CUDA
         fi
         if [ -f "/usr/local/cuda9/version.txt" ];then
           CUDA=`cat /usr/local/cuda9/version.txt | grep 'CUDA Version'|awk -F '[ .]' '{print $3}'`
           tmp_cuda9=$CUDA
         fi
         if [ -f "/usr/local/cuda10/version.txt" ];then
           CUDA=`cat /usr/local/cuda10/version.txt | grep 'CUDA Version'|awk -F '[ .]' '{print $3}'`
           tmp_cuda10=$CUDA
         fi
       fi

       if [ "$tmp_cuda" != "" ];then
         echo "æ£€æµ‹ç»“æžœï¼šæ‰¾åˆ°CUDA $tmp_cuda"
       fi
       if [ "$tmp_cudai8" != "" ];then
         echo "æ£€æµ‹ç»“æžœï¼šæ‰¾åˆ°CUDA $tmp_cuda8"
       fi
       if [ "$tmp_cuda9" != "" ];then
         echo "æ£€æµ‹ç»“æžœï¼šæ‰¾åˆ°CUDA $tmp_cuda9"
       fi
       if [ "$tmp_cuda10" != "" ];then
         echo "æ£€æµ‹ç»“æžœï¼šæ‰¾åˆ°CUDA $tmp_cuda10"
       fi

       if [ "$CUDA" == "" ];then
            echo "æ£€æµ‹ç»“æžœï¼šæ²¡æœ‰åœ¨å¸¸è§„è·¯å¾„ä¸‹æ‰¾åˆ°cuda/version.txtæ–‡ä»¶"
            while true
            do
                read -p "è¯·è¾“å…¥cuda/version.txtçš„è·¯å¾„:" cuda_version
                if [ "$cuda_version" == "" || ! -f "$cuda_version" ];then
                    read -p "ä»æœªæ‰¾åˆ°CUDAï¼Œè¾“å…¥yå°†å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddleï¼Œè¾“å…¥nå¯é‡æ–°å½•å…¥CUDAè·¯å¾„ï¼Œè¯·è¾“å…¥ï¼ˆy/nï¼‰" cpu_option
                    cpu_option=`echo $cpu_option | tr 'A-Z' 'a-z'`
                    if [ "$cpu_option" == "y" || "$cpu_option" == "" ];then
                        GPU='cpu'
                        break
                    else
                        echo "é‡æ–°è¾“å…¥..."
                    fi
                else
                    CUDA=`cat $cuda_version | grep 'CUDA Version'|awk -F '[ .]' '{print $3}'`
                    if [ "$CUDA" == "" ];then
                        echo "æœªèƒ½åœ¨version.txtä¸­æ‰¾åˆ°CUDAç›¸å…³ä¿¡æ¯"
                    else
                        break
                    fi
                fi
            done
            if [ "$GPU" == "cpu" ];then
                break
            fi
       fi

       if [ "$CUDA" == "8" ] || [ "$CUDA" == "9" ] || [ "$CUDA" == "10" ];then
          echo "æ‚¨çš„CUDAç‰ˆæœ¬æ˜¯${CUDA}"
          break
       else
          echo "ç›®å‰æ”¯æŒCUDA8/9/10ï¼Œæš‚ä¸æ”¯æŒæ‚¨çš„CUDA${CUDA}ï¼Œå°†ä¸ºæ‚¨å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddle"
          echo
          use_cpu
       fi

       if [ "$GPU" == "cpu" ];then
          break
       fi
   done
}

function checkLinuxMathLibrary(){
  while true
    do
      if [ "$GPU" == "gpu" ];then
        math='mkl'
        echo "æ£€æµ‹åˆ°æ‚¨çš„æœºå™¨ä¸Šé…å¤‡GPUï¼ŒæŽ¨èæ‚¨ä½¿ç”¨mklæ•°å­¦åº“"
        break
      else
        read -p "è¯·è¾“å…¥æ‚¨å¸Œæœ›ä½¿ç”¨çš„æ•°å­¦åº“ï¼š
            1ï¼šopenblas ä¸€ä¸ªé«˜æ€§èƒ½å¤šæ ¸ BLAS åº“
            2ï¼šmklï¼ˆæŽ¨èï¼‰ è‹±ç‰¹å°”æ•°å­¦æ ¸å¿ƒå‡½æ•°åº“
            => è¯·è¾“å…¥æ•°å­—1æˆ–2ã€‚å¦‚è¾“å…¥å…¶ä»–å­—ç¬¦æˆ–ç›´æŽ¥å›žè½¦ï¼Œå°†ä¼šé»˜è®¤é€‰æ‹©ã€ 2. mkl ã€‘ ã€‚è¯·åœ¨è¿™é‡Œè¾“å…¥å¹¶å›žè½¦ï¼š" math
          if [ "$math" == "" ];then
            math="mkl"
            echo "æ‚¨é€‰æ‹©äº†æ•°å­—ã€2ã€‘"
            break
          fi
          if [ "$math" == "1" ];then
            math=openblas
            echo "æ‚¨é€‰æ‹©äº†æ•°å­—ã€1ã€‘"
            break
          elif [ "$math" == "2" ];then
            math=mkl
            echo "æ‚¨é€‰æ‹©äº†æ•°å­—ã€2ã€‘"
            break
          fi
          echo "è¾“å…¥é”™è¯¯ï¼Œè¯·å†æ¬¡è¾“å…¥"
      fi
    done
}

function checkLinuxPaddleVersion(){
  read -n1 -p "è¯·æŒ‰å›žè½¦é”®ç»§ç»­..."
  while true
    do
      read -p "
               1. å¼€å‘ç‰ˆï¼šå¯¹åº”Githubä¸Šdevelopåˆ†æ”¯ï¼Œå¦‚æ‚¨éœ€è¦å¼€å‘ã€æˆ–å¸Œæœ›ä½¿ç”¨PaddlePaddleæœ€æ–°åŠŸèƒ½ï¼Œè¯·é€‰ç”¨æ­¤ç‰ˆæœ¬
               2. ç¨³å®šç‰ˆï¼ˆæŽ¨èï¼‰ï¼šå¦‚æ‚¨æ— ç‰¹æ®Šå¼€å‘éœ€æ±‚ï¼Œå»ºè®®ä½¿ç”¨æ­¤ç‰ˆæœ¬ï¼Œç›®å‰æœ€æ–°çš„ç‰ˆæœ¬å·ä¸º ${release_version}
                => è¯·è¾“å…¥æ•°å­—1æˆ–2ã€‚å¦‚è¾“å…¥å…¶ä»–å­—ç¬¦æˆ–ç›´æŽ¥å›žè½¦ï¼Œå°†ä¼šé»˜è®¤é€‰æ‹©ã€ 2. ç¨³å®šç‰ˆ ã€‘ ã€‚è¯·åœ¨è¿™é‡Œè¾“å…¥å¹¶å›žè½¦ï¼š" paddle_version
        if [ "$paddle_version" == "" ];then
          paddle_version="2"
          echo "æ‚¨é€‰æ‹©äº†æ•°å­—ã€2ã€‘ï¼Œä¸ºæ‚¨å®‰è£…release-${release_version}"
          break
        fi
        if [ "$paddle_version" == "1" ];then
          echo "æ‚¨é€‰æ‹©äº†æ•°å­—ã€1ã€‘ï¼Œå°†ä¸ºæ‚¨å®‰è£…å¼€å‘ç‰ˆ"
          break
        elif [ "$paddle_version" == "2" ];then
          echo "æ‚¨é€‰æ‹©äº†æ•°å­—ã€2ã€‘ï¼Œä¸ºæ‚¨å®‰è£…release-${release_version}"
          break
        fi
        echo "è¾“å…¥é”™è¯¯ï¼Œè¯·å†æ¬¡è¾“å…¥"
    done
}

function checkPythonVirtualenv(){
  while true
    do
      read -p "
                æ˜¯å¦ä½¿ç”¨python  virtualenvè™šçŽ¯å¢ƒå®‰è£…(y/n)": check_virtualenv
    case $check_virtualenv in
      y)
        echo "ä¸ºæ‚¨ä½¿ç”¨pythonè™šçŽ¯å¢ƒå®‰è£…"
        ;;
      n)
        break
        ;;
      *)
        continue
        ;;
    esac

    virtualenv_path=`which virtualenv 2>&1`
    if [ "$virtualenv_path" == "" ];then
      $python_path -m pip install virtualenv
      if [ "$?" != '0' ];then
        echo "å®‰è£…è™šæ‹ŸçŽ¯å¢ƒå¤±è´¥,è¯·æ£€æŸ¥æœ¬åœ°çŽ¯å¢ƒ"
      fi
    fi

    while true
      do
        read -p "è¯·è¾“å…¥è™šæ‹ŸçŽ¯å¢ƒåå­—ï¼š" virtualenv_name
        if [ "$virtualenv_name" == "" ];then
          echo "ä¸èƒ½ä¸ºç©º"
          continue
        fi
        break
    done

    virtualenv -p $python_path ${virtualenv_name}
    if [ "$?" != 0 ];then
      echo "åˆ›å»ºè™šçŽ¯å¢ƒå¤±è´¥,è¯·æ£€æŸ¥çŽ¯å¢ƒ"
      exit 2
    fi
    cd ${virtualenv_name}
    source ./bin/activate

    if [ "$?" == 0 ];then
      use_virtualenv=
      python_path=`which python`
      break
    else
      echo "åˆ›å»ºè™šçŽ¯å¢ƒå¤±è´¥,è¯·æ£€æŸ¥çŽ¯å¢ƒ"
      exit 2
    fi
  done
}

function checkLinuxPython(){
  python_path=`which python 2>/dev/null`
  while true
    do
  if [ "$python_path" == '' ];then
    while true
      do
        read -p "æ²¡æœ‰æ‰¾åˆ°é»˜è®¤çš„pythonç‰ˆæœ¬,è¯·è¾“å…¥è¦å®‰è£…çš„pythonè·¯å¾„:"  python_path
        python_path=`$python_path -V 2>&1` #add 2>&1
        if [ "$python_path" != "" ];then
          break
        else
          echo "è¾“å…¥è·¯å¾„æœ‰è¯¯,æœªæ‰¾åˆ°pyrhon"
        fi
    done
  fi

  python_version=`$python_path -V 2>&1|awk -F '[ .]' '{print $2$3}'`
  pip_version=`$python_path -m pip -V|awk -F '[ .]' '{print $2}'`
  while true
    do
      read -p "
                æ‰¾åˆ°pythonç‰ˆæœ¬$python_version,ä½¿ç”¨è¯·è¾“å…¥y,é€‰æ‹©å…¶ä»–ç‰ˆæœ¬è¯·è¾“n(y/n):"  check_python
      case $check_python in
        n)
          read -p "è¯·æŒ‡å®šæ‚¨çš„pythonè·¯å¾„:" new_python_path
          python_V=`$new_python_path -V 2>&1` # 2>/dev/null --> 2>&1
          if [ "$python_V" != "" ];then
            python_path=$new_python_path
            python_version=`$python_path -V 2>&1|awk -F '[ .]' 'NR==1{print $2$3}'`
            echo $python_path
            pip_version=`$python_path -m pip -V|awk -F '[ .]' 'NR==1{print $2}'`
            echo "æ‚¨çš„pythonç‰ˆæœ¬ä¸º${python_version}"
            break
          else
            echo è¾“å…¥æœ‰è¯¯,æœªæ‰¾åˆ°pythonè·¯å¾„
          fi
          ;;
        y)
          break
          ;;
        *)
          echo "è¾“å…¥æœ‰è¯¯ï¼Œè¯·é‡æ–°è¾“å…¥."
          continue
          ;;
      esac
  done

  if [ "$pip_version" -lt 10 ];then
    echo "æ‚¨çš„pipç‰ˆæœ¬å°äºŽ9.0.1  è¯·å‡çº§pip (pip install --upgrade pip)"
    exit 0
  fi


  if [ "$python_version" == "27" ];then
     python_version_all=`$python_path -V 2>&1|awk -F '[ .]' '{print $4}'`
     if [[ $python_version_all -le 15 ]];then
        echo "Python2ç‰ˆæœ¬å°äºŽ2.7.15,è¯·æ›´æ–°Python2ç‰ˆæœ¬æˆ–ä½¿ç”¨Python3"
        exit 0
      fi
     uncode=`$python_path -c "import pip._internal;print(pip._internal.pep425tags.get_supported())"|grep "cp27mu"`
     if [[ "$uncode" == "" ]];then
        uncode=
     else
        uncode=u
     fi
  fi

  version_list=`echo "${python_list[@]}" | grep "$python_version" `
  if [ "$version_list" == "" ];then
    echo "æ‰¾ä¸åˆ°å¯ç”¨çš„ pip, æˆ‘ä»¬åªæ”¯æŒPython27/35/36/37åŠå…¶å¯¹åº”çš„pip, è¯·é‡æ–°è¾“å…¥ï¼Œ æˆ–ä½¿ç”¨ctrl + cé€€å‡º "
  else
    break
  fi
  done
}


function PipLinuxInstall(){
  wheel_cpu_release="http://paddle-wheel.bj.bcebos.com/${release_version}-${GPU}-${math}/paddlepaddle-${release_version}-cp${python_version}-cp${python_version}m${uncode}-linux_x86_64.whl"
  wheel_gpu_release="http://paddle-wheel.bj.bcebos.com/${release_version}-gpu-cuda${CUDA}-cudnn${CUDNN}-${math}/paddlepaddle_gpu-${release_version}.post${CUDA}${CUDNN}-cp${python_version}-cp${python_version}m${uncode}-linux_x86_64.whl"
  wheel_cpu_develop="http://paddle-wheel.bj.bcebos.com/0.0.0-cpu-${math}/paddlepaddle-0.0.0-cp${python_version}-cp${python_version}m${uncode}-linux_x86_64.whl"
  wheel_gpu_develop="http://paddle-wheel.bj.bcebos.com/0.0.0-gpu-cuda${CUDA}-cudnn${CUDNN}-${math}/paddlepaddle_gpu-0.0.0-cp${python_version}-cp${python_version}m${uncode}-linux_x86_64.whl"


  if [[ "$paddle_version" == "2" ]];then
    if [[ "$GPU" == "gpu" ]];then
          rm -rf `echo $wheel_cpu_release|awk -F '/' '{print $NF}'`
          echo $wheel_gpu_release
          wget -q $wheel_gpu_release
          if [ "$?" == "0" ];then
            $python_path -m pip install -U ${use_virtualenv} -i https://mirrors.aliyun.com/pypi/simple --trusted-host=mirrors.aliyun.com $wheel_gpu_release
            if [ "$?" == 0 ];then
              echo å®‰è£…æˆåŠŸ
              exit 0
            else
              echo å®‰è£…å¤±è´¥
              exit 1
            fi
          else
            echo paddlepaddle whlåŒ…ä¸‹è½½å¤±è´¥
            echo "wget err: $wheel_gpu_release"
            exit 1
          fi
    else
        echo $wheel_cpu_release
        rm -rf `echo $wheel_cpu_release|awk -F '/' '{print $NF}'`
        wget -q $wheel_cpu_release
        if [ "$?" == "0" ];then
          $python_path -m pip install -U ${use_virtualenv} -i https://mirrors.aliyun.com/pypi/simple --trusted-host=mirrors.aliyun.com $wheel_cpu_release
          if [ "$?" == 0 ];then
              echo å®‰è£…æˆåŠŸ
              exit 0
            else
              echo å®‰è£…å¤±è´¥
              exit 1
            fi
        else
          echo paddlepaddle whlåŒ…ä¸‹è½½å¤±è´¥
          echo "wget err: $wheel_cpu_release"
          exit 1
        fi
    fi
  fi
  if [[ "$GPU" == "gpu" ]];then
        echo $wheel_gpu_develop
        rm -rf `echo $wheel_gpu_develop|awk -F '/' '{print $NF}'`
        wget -q $wheel_gpu_develop
        if [ "$?" == "0" ];then
          echo $python_path,111
          $python_path -m pip install -U ${use_virtualenv} -i https://mirrors.aliyun.com/pypi/simple --trusted-host=mirrors.aliyun.com $wheel_gpu_develop
          if [ "$?" == 0 ];then
              echo å®‰è£…æˆåŠŸ
              exit 0
            else
              echo å®‰è£…å¤±è´¥
              exit 1
            fi
        else
          echo paddlepaddle whlåŒ…ä¸‹è½½å¤±è´¥
          echo "wget err: $wheel_gpu_develop"
          exit 1
        fi
  else
        echo $wheel_cpu_develop
        rm -rf `echo $wheel_cpu_develop|awk -F '/' '{print $NF}'`
        wget -q $wheel_cpu_develop
        if [ "$?" == "0" ];then
          $python_path -m pip install -U ${use_virtualenv} -i https://mirrors.aliyun.com/pypi/simple --trusted-host=mirrors.aliyun.com $wheel_cpu_develop
          if [ "$?" == 0 ];then
              echo å®‰è£…æˆåŠŸ
              exit 0
            else
              echo å®‰è£…å¤±è´¥
              exit 1
            fi
        else
          echo paddlepaddle whlåŒ…ä¸‹è½½å¤±è´¥
          echo "wget err: $wheel_cpu_develop"
          exit 1
        fi
    fi
}


function checkLinuxGPU(){
  read -n1 -p "å³å°†æ£€æµ‹æ‚¨çš„æœºå™¨æ˜¯å¦å«GPUï¼Œè¯·æŒ‰å›žè½¦é”®ç»§ç»­..."
  echo
  which nvidia-smi >/dev/null 2>&1
  if [ "$?" != "0" ];then
    GPU='cpu'
    echo "æœªåœ¨æœºå™¨ä¸Šæ‰¾åˆ°GPUï¼Œæˆ–PaddlePaddleæš‚ä¸æ”¯æŒæ­¤åž‹å·çš„GPU"
  else
    GPU='gpu'
    echo "å·²åœ¨æ‚¨çš„æœºå™¨ä¸Šæ‰¾åˆ°GPUï¼Œå³å°†ç¡®è®¤CUDAå’ŒCUDNNç‰ˆæœ¬..."
    echo
  fi
  if [ "$GPU" == 'gpu' ];then
    checkLinuxCUDA
    checkLinuxCUDNN
  fi
}

function linux(){
gpu_list=(
"GeForce 410M"
"GeForce 610M"
"GeForce 705M"
"GeForce 710M"
"GeForce 800M"
"GeForce 820M"
"GeForce 830M"
"GeForce 840M"
"GeForce 910M"
"GeForce 920M"
"GeForce 930M"
"GeForce 940M"
"GeForce GT 415M"
"GeForce GT 420M"
"GeForce GT 430"
"GeForce GT 435M"
"GeForce GT 440"
"GeForce GT 445M"
"GeForce GT 520"
"GeForce GT 520M"
"GeForce GT 520MX"
"GeForce GT 525M"
"GeForce GT 540M"
"GeForce GT 550M"
"GeForce GT 555M"
"GeForce GT 610"
"GeForce GT 620"
"GeForce GT 620M"
"GeForce GT 625M"
"GeForce GT 630"
"GeForce GT 630M"
"GeForce GT 635M"
"GeForce GT 640"
"GeForce GT 640 (GDDR5)"
"GeForce GT 640M"
"GeForce GT 640M LE"
"GeForce GT 645M"
"GeForce GT 650M"
"GeForce GT 705"
"GeForce GT 720"
"GeForce GT 720M"
"GeForce GT 730"
"GeForce GT 730M"
"GeForce GT 735M"
"GeForce GT 740"
"GeForce GT 740M"
"GeForce GT 745M"
"GeForce GT 750M"
"GeForce GTS 450"
"GeForce GTX 1050"
"GeForce GTX 1060"
"GeForce GTX 1070"
"GeForce GTX 1080"
"GeForce GTX 1080 Ti"
"GeForce GTX 460"
"GeForce GTX 460M"
"GeForce GTX 465"
"GeForce GTX 470"
"GeForce GTX 470M"
"GeForce GTX 480"
"GeForce GTX 480M"
"GeForce GTX 485M"
"GeForce GTX 550 Ti"
"GeForce GTX 560M"
"GeForce GTX 560 Ti"
"GeForce GTX 570"
"GeForce GTX 570M"
"GeForce GTX 580"
"GeForce GTX 580M"
"GeForce GTX 590"
"GeForce GTX 650"
"GeForce GTX 650 Ti"
"GeForce GTX 650 Ti BOOST"
"GeForce GTX 660"
"GeForce GTX 660M"
"GeForce GTX 660 Ti"
"GeForce GTX 670"
"GeForce GTX 670M"
"GeForce GTX 670MX"
"GeForce GTX 675M"
"GeForce GTX 675MX"
"GeForce GTX 680"
"GeForce GTX 680M"
"GeForce GTX 680MX"
"GeForce GTX 690"
"GeForce GTX 750"
"GeForce GTX 750 Ti"
"GeForce GTX 760"
"GeForce GTX 760M"
"GeForce GTX 765M"
"GeForce GTX 770"
"GeForce GTX 770M"
"GeForce GTX 780"
"GeForce GTX 780M"
"GeForce GTX 780 Ti"
"GeForce GTX 850M"
"GeForce GTX 860M"
"GeForce GTX 870M"
"GeForce GTX 880M"
"GeForce GTX 950"
"GeForce GTX 950M"
"GeForce GTX 960"
"GeForce GTX 960M"
"GeForce GTX 965M"
"GeForce GTX 970"
"GeForce GTX 970M"
"GeForce GTX 980"
"GeForce GTX 980M"
"GeForce GTX 980 Ti"
"GeForce GTX TITAN"
"GeForce GTX TITAN Black"
"GeForce GTX TITAN X"
"GeForce GTX TITAN Z"
"Jetson TK1"
"Jetson TX1"
"Jetson TX2"
"Mobile Products"
"NVIDIA NVS 310"
"NVIDIA NVS 315"
"NVIDIA NVS 510"
"NVIDIA NVS 810"
"NVIDIA TITAN V"
"NVIDIA TITAN X"
"NVIDIA TITAN Xp"
"NVS 4200M"
"NVS 5200M"
"NVS 5400M"
"Quadro 410"
"Quadro GP100"
"Quadro K1100M"
"Quadro K1200"
"Quadro K2000"
"Quadro K2000D"
"Quadro K2100M"
"Quadro K2200"
"Quadro K2200M"
"Quadro K3100M"
"Quadro K4000"
"Quadro K4100M"
"Quadro K420"
"Quadro K4200"
"Quadro K4200M"
"Quadro K5000"
"Quadro K500M"
"Quadro K5100M"
"Quadro K510M"
"Quadro K5200"
"Quadro K5200M"
"Quadro K600"
"Quadro K6000"
"Quadro K6000M"
"Quadro K610M"
"Quadro K620"
"Quadro K620M"
"Quadro M1000M"
"Quadro M1200"
"Quadro M2000"
"Quadro M2000M"
"Quadro M2200"
"Quadro M3000M"
"Quadro M4000"
"Quadro M4000M"
"Quadro M5000"
"Quadro M5000M"
"Quadro M500M"
"Quadro M520"
"Quadro M5500M"
"Quadro M6000"
"Quadro M6000 24GB"
"Quadro M600M"
"Quadro M620"
"Quadro Mobile Products"
"Quadro P1000"
"Quadro P2000"
"Quadro P3000"
"Quadro P400"
"Quadro P4000"
"Quadro P5000"
"Quadro P600"
"Quadro P6000"
"Quadro Plex 7000"
"Tegra K1"
"Tegra X1"
"Tesla C2050/C2070"
"Tesla C2075"
"Tesla Data Center Products"
"Tesla K10"
"Tesla K20"
"Tesla K40"
"Tesla K80"
"Tesla M40"
"Tesla M60"
"Tesla P100"
"Tesla P4"
"Tesla P40"
"Tesla V100")

  echo "Step 2. æ£€æµ‹GPUåž‹å·å’ŒCUDA/cuDNNç‰ˆæœ¬"
  echo
  checkLinuxGPU
  echo
  echo "Step 3. æ£€æµ‹æ•°å­¦åº“"
  echo
  checkLinuxMathLibrary
  echo
  echo "Step 4. é€‰æ‹©è¦å®‰è£…çš„PaddlePaddleç‰ˆæœ¬"
  echo
  checkLinuxPaddleVersion
  echo
  echo "Step 5. æ£€æµ‹pipç‰ˆæœ¬"
  echo
  checkLinuxPython
  echo
  echo "Step 6.æ˜¯å¦ä½¿ç”¨Pythonçš„è™šæ‹ŸçŽ¯å¢ƒ"
  use_virtualenv="--user"
  checkPythonVirtualenv
  echo "*********************2. å¼€å§‹å®‰è£…*****************************"
  PipLinuxInstall
  if [ "$check_virtualenv" == 'y' ];then
    echo "è™šçŽ¯å¢ƒåˆ›å»ºæˆåŠŸï¼Œè¯·cd è¿›å…¥${virtualenv_name}, æ‰§è¡Œ source bin/activateã€€è¿›å…¥è™šçŽ¯å¢ƒã€‚é€€å‡ºè™šçŽ¯å¢ƒæ‰§è¡Œ deactivateå‘½ä»¤ã€‚
  æ›´å¤šè™šçŽ¯å¢ƒä½¿ç”¨æ–¹æ³•è¯·å‚è€ƒvirtualenvå®˜ç½‘:https://virtualenv.pypa.io/en/latest/"
  fi
}

function clearMacPythonEnv(){
   python_version=""
   python_brief_version=""
   python_root=""
}

function checkMacPython2(){
    while true
       do
          python_min="2.7.15"
          python_version=`$python_root --version 2>&1 1>&1`
          if [[ $? == "0" ]];then
               if [ "$python_version" == "" ] || ( [ "$python_root" == "/usr/bin/python" ] && ( [ "$python_version" \< "$python_min" ] || ( [ "$python_version" \> "$python_min" ] && [ ${#python_version} -lt ${#python_min} ] ) ) );then
                    clearMacPythonEnv
               elif [[ "$python_version" < "2.7.15" ]];then
                    echo -e "          => åœ¨æ‚¨çš„çŽ¯å¢ƒä¸­æ‰¾åˆ° \033[32m[ $python_version ]\033[0m,æ­¤ç‰ˆæœ¬å°äºŽ2.7.15ä¸å»ºè®®ä½¿ç”¨,è¯·é€‰æ‹©å…¶ä»–ç‰ˆæœ¬."
                    exit
               else
                    check_python=`echo $python_version | grep "Python 2"`
                    if [[ -n "$check_python" ]];then
                       while true
                         do
                           echo -e "          => åœ¨æ‚¨çš„çŽ¯å¢ƒä¸­æ‰¾åˆ° \033[32m[ $python_version ]\033[0m, ç¡®è®¤ä½¿ç”¨æ­¤ç‰ˆæœ¬è¯·è¾“å…¥yï¼›å¦‚æ‚¨å¸Œæœ›è‡ªå®šä¹‰Pythonè·¯å¾„è¯·è¾“å…¥nã€‚è¯·åœ¨è¿™é‡Œè¾“å…¥ï¼ˆy/nï¼‰å¹¶å›žè½¦: "
                           read -p "" use_python
                           echo
                           use_python=`echo $use_python | tr 'A-Z' 'a-z'`
                           if [[ "$use_python" == "y" ]]||[[ "$use_python" == "" ]];then
                                use_python="y"
                                break
                           elif [[ "$use_python" == "n" ]];then
                                clearMacPythonEnv
                                break
                           else
                               red "            è¾“å…¥é”™è¯¯ï¼Œè¯·é‡æ–°è¾“å…¥(y/n)"
                           fi
                       done
                       if [[ "$use_python" == "y" ]];then
                         return 0
                       fi
                    else
                       red "          æ‚¨è¾“å…¥Pythonçš„ä¸æ˜¯Python2"
                       clearMacPythonEnv
                    fi
               fi
          else
               clearMacPythonEnv
               red "          => æœªèƒ½åœ¨å¸¸è§„è·¯å¾„ä¸‹æ‰¾åˆ°å¯ç”¨çš„Python2ï¼Œè¯·ä½¿ç”¨ctrl+cå‘½ä»¤é€€å‡ºå®‰è£…ç¨‹åºï¼Œå¹¶ä½¿ç”¨brewæˆ–pypi.orgä¸‹è½½å®‰è£…Python2ï¼ˆæ³¨æ„Pythonç‰ˆæœ¬ä¸èƒ½ä½ŽäºŽ2.7.15ï¼‰"
               read -p "          å¦‚å¸Œæœ›è‡ªå®šä¹‰Pythonè·¯å¾„ï¼Œè¯·è¾“å…¥è·¯å¾„
          å¦‚æžœå¸Œæœ›é‡æ–°é€‰æ‹©Pythonç‰ˆæœ¬ï¼Œè¯·å›žè½¦ï¼š" python_root
               echo
               if [[ "$python_root" == "" ]];then
                     python_V=""
                     clearMacPythonEnv
                     return 1
               fi
          fi
       done
}

function checkMacPython3(){
    while true
       do
          python_min="2.7.15"
          python_version=`$python_root --version 2>&1 1>&1`
          if [[ $? == "0" ]];then
               if [ "$python_version" == "" ] || ( [ "$python_root" == "/usr/bin/python" ] && ( [ "$python_version" \< "$python_min" ] || ( [ "$python_version" \> "$python_min" ] && [ ${#python_version} -lt ${#python_min} ] ) ) );then
                    clearMacPythonEnv
               else
                    check_python=`echo $python_version | grep "Python 3"`
                    if [[ -n "$check_python" ]];then
                       while true
                         do
                           echo -e "          => åœ¨æ‚¨çš„çŽ¯å¢ƒä¸­æ‰¾åˆ° \033[32m[ $python_version ]\033[0m, ç¡®è®¤ä½¿ç”¨æ­¤ç‰ˆæœ¬è¯·è¾“å…¥yï¼›å¦‚æ‚¨å¸Œæœ›è‡ªå®šä¹‰Pythonè·¯å¾„è¯·è¾“å…¥nã€‚è¯·åœ¨è¿™é‡Œè¾“å…¥ï¼ˆy/nï¼‰å¹¶å›žè½¦: "
                           read -p "" use_python
                           echo
                           use_python=`echo $use_python | tr 'A-Z' 'a-z'`
                           if [[ "$use_python" == "y" ]]||[[ "$use_python" == "" ]];then
                                use_python="y"
                                break
                           elif [[ "$use_python" == "n" ]];then
                                clearMacPythonEnv
                                break
                           else
                               red "            è¾“å…¥é”™è¯¯ï¼Œè¯·é‡æ–°è¾“å…¥(y/n)"
                           fi
                       done
                       if [[ "$use_python" == "y" ]];then
                         return 0
                       fi
                    else
                       red "          æ‚¨è¾“å…¥Pythonçš„ä¸æ˜¯Python3"
                       clearMacPythonEnv
                    fi
               fi
          else
               clearMacPythonEnv
               red "          => æœªèƒ½åœ¨å¸¸è§„è·¯å¾„ä¸‹æ‰¾åˆ°å¯ç”¨çš„Python3ï¼Œè¯·ä½¿ç”¨ctrl+cå‘½ä»¤é€€å‡ºå®‰è£…ç¨‹åºï¼Œå¹¶ä½¿ç”¨brewæˆ–pypi.orgä¸‹è½½å®‰è£…Python3ï¼ˆæ³¨æ„Pythonç‰ˆæœ¬ä¸èƒ½ä½ŽäºŽ3.5.x)"
               read -p "          å¦‚å¸Œæœ›è‡ªå®šä¹‰Pythonè·¯å¾„ï¼Œè¯·è¾“å…¥è·¯å¾„
          å¦‚æžœå¸Œæœ›é‡æ–°é€‰æ‹©Pythonç‰ˆæœ¬ï¼Œè¯·å›žè½¦ï¼š" python_root
               echo
               if [[ "$python_root" == "" ]];then
                     python_V=""
                     clearMacPythonEnv
                     return 1
               fi
          fi
       done
}

function checkMacPaddleVersion(){
    echo
    yellow "          ç›®å‰PaddlePaddleåœ¨MacOSçŽ¯å¢ƒä¸‹åªæä¾›ç¨³å®šç‰ˆï¼Œæœ€æ–°çš„ç‰ˆæœ¬å·ä¸º ${release_version}"
    echo
    paddle_version="2"
    echo
    yellow "          æˆ‘ä»¬å°†ä¼šä¸ºæ‚¨å®‰è£…PaddlePaddleç¨³å®šç‰ˆï¼Œè¯·æŒ‰å›žè½¦é”®ç»§ç»­... "
    read -n1 -p ""
    echo
}
function initCheckMacPython2(){
   echo
   yellow "          æ‚¨é€‰æ‹©äº†Python "$python_V"ï¼Œæ­£åœ¨å¯»æ‰¾ç¬¦åˆè¦æ±‚çš„Python 2ç‰ˆæœ¬"
   echo
   python_root=`which python2.7`
   if [[ "$python_root" == "" ]];then
        python_root=`which python`
   fi
   checkMacPython2
   if [[ "$?" == "1" ]];then
        return 1
   else
        return 0
   fi
}

function initCheckMacPython3(){
   echo
   yellow "          æ‚¨é€‰æ‹©äº†Python "$python_V"ï¼Œæ­£åœ¨å¯»æ‰¾ç¬¦åˆæ‚¨è¦æ±‚çš„Python 3ç‰ˆæœ¬"
   echo
   python_root=`which python3`
   checkMacPython3
   if [[ "$?" == "1" ]];then
        return 1
   else
        return 0
   fi
}

function checkMacPip(){
   if [[ "$python_V" == "2" ]]||[[ "$python_V" == "3" ]];then

       python_brief_version=`$python_root -m pip -V |awk -F "[ |)]" '{print $6}'|sed 's#\.##g'`
       if [[ ${python_brief_version} == "" ]];then
            red "æ‚¨è¾“å…¥çš„pythonï¼š${python_root} å¯¹åº”çš„pipä¸å¯ç”¨ï¼Œè¯·æ£€æŸ¥æ­¤pipæˆ–é‡æ–°é€‰æ‹©å…¶ä»–python"
            echo
            return 1
       fi
       pip_version=`$python_root -m pip -V |awk -F '[ .]' '{print $2}'`
       if [[ 9 -le ${pip_version} ]];then
            :
       else
            red "æ‚¨çš„pipç‰ˆæœ¬è¿‡ä½Žï¼Œè¯·å®‰è£…pip 9.0.1åŠä»¥ä¸Šçš„ç‰ˆæœ¬"
            echo
            return 1
       fi
       if [[ "$python_brief_version" == "" ]];then
            clearMacPythonEnv
            red "æ‚¨çš„ $python_root å¯¹åº”çš„pipå­˜åœ¨é—®é¢˜ï¼Œè¯·æŒ‰ctrl + cé€€å‡ºåŽé‡æ–°å®‰è£…pipï¼Œæˆ–åˆ‡æ¢å…¶ä»–pythonç‰ˆæœ¬"
            echo
            return 1
       else
            if [[ $python_brief_version == "27" ]];then
               uncode=`$python_root -c "import pip._internal;print(pip._internal.pep425tags.get_supported())"|grep "cp27"`
               if [[ $uncode == "" ]];then
                  uncode="mu"
               else
                  uncode="m"
               fi
            fi
            version_list=`echo "${python_list[@]}" | grep "$python_brief_version" `
            if [[ "$version_list" != "" ]];then
               return 0
             else
               red "æœªæ‰¾åˆ°å¯ç”¨çš„pipæˆ–pip3ã€‚PaddlePaddleç›®å‰æ”¯æŒï¼šPython2.7/3.5/3.6/3.7åŠå…¶å¯¹åº”çš„pip, è¯·é‡æ–°è¾“å…¥ï¼Œæˆ–ä½¿ç”¨ctrl + cé€€å‡º"
               echo
               clearMacPythonEnv
               return 1
            fi

       fi
   fi
}

function checkMacPythonVersion(){
  while true
    do
       read -n1 -p "Step 3. é€‰æ‹©Pythonç‰ˆæœ¬ï¼Œè¯·æŒ‰å›žè½¦é”®ç»§ç»­..."
       echo
       yellow "          2. ä½¿ç”¨python 2.x"
       yellow "          3. ä½¿ç”¨python 3.x"
       read -p "          => è¯·è¾“å…¥æ•°å­—2æˆ–3ã€‚å¦‚è¾“å…¥å…¶ä»–å­—ç¬¦æˆ–ç›´æŽ¥å›žè½¦ï¼Œå°†ä¼šé»˜è®¤ä½¿ç”¨ã€Python 2 ã€‘ã€‚è¯·åœ¨è¿™é‡Œè¾“å…¥å¹¶å›žè½¦ï¼š" python_V
       if [[ "$python_V" == "" ]];then
            python_V="2"
       fi
       if [[ "$python_V" == "2" ]];then
            initCheckMacPython2
            if [[ "$?" == "0" ]];then
                checkMacPip
                if [[ "$?" == "0" ]];then
                    return 0
                else
                    :
                fi
            else
                :
            fi
       elif [[ "$python_V" == "3" ]];then
            initCheckMacPython3
            if [[ "$?" == "0" ]];then
                checkMacPip
                if [[ "$?" == "0" ]];then
                    return 0
                else
                    :
                fi
            else
                :
            fi
       else
            red "è¾“å…¥é”™è¯¯ï¼Œè¯·é‡æ–°è¾“å…¥"
       fi
  done
}


function checkMacGPU(){
    read -n1 -p "Step 5. é€‰æ‹©CPU/GPUç‰ˆæœ¬ï¼Œè¯·æŒ‰å›žè½¦é”®ç»§ç»­..."
    echo
    if [[ $GPU != "" ]];then
        yellow "          MacOSçŽ¯å¢ƒä¸‹ï¼Œæš‚æœªæä¾›GPUç‰ˆæœ¬çš„PaddlePaddleå®‰è£…åŒ…ï¼Œå°†ä¸ºæ‚¨å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddle"
    else
        yellow "          MacOSçŽ¯å¢ƒä¸‹ï¼Œæš‚æœªæä¾›GPUç‰ˆæœ¬çš„PaddlePaddleå®‰è£…åŒ…ï¼Œå°†ä¸ºæ‚¨å®‰è£…CPUç‰ˆæœ¬çš„PaddlePaddle"
        GPU=cpu
    fi
    echo
}

function macos() {
  path='http://paddlepaddle.org/download?url='

  while true
      do

        checkMacPaddleVersion

        checkMacPythonVersion

        checkMacGPU


        green "*********************2. å¼€å§‹å®‰è£…*****************************"
        echo
        yellow "å³å°†ä¸ºæ‚¨ä¸‹è½½å¹¶å®‰è£…PaddlePaddleï¼Œè¯·æŒ‰å›žè½¦é”®ç»§ç»­..."
        read -n1 -p ""
        if [[ $paddle_version == "2" ]];then
            $python_root -m pip install -U  paddlepaddle
            if [[ $? == "0" ]];then
               green "å®‰è£…æˆåŠŸï¼Œå¯ä»¥ä½¿ç”¨: ${python_root} æ¥å¯åŠ¨å®‰è£…äº†PaddlePaddleçš„Pythonè§£é‡Šå™¨"
               break
            else
               rm  $whl_cpu_release
               red "æœªèƒ½æ­£å¸¸å®‰è£…PaddlePaddleï¼Œè¯·å°è¯•æ›´æ¢æ‚¨è¾“å…¥çš„pythonè·¯å¾„ï¼Œæˆ–è€…ctrl + cé€€å‡ºåŽè¯·æ£€æŸ¥æ‚¨ä½¿ç”¨çš„pythonå¯¹åº”çš„pipæˆ–pipæºæ˜¯å¦å¯ç”¨"
               echo""
               echo "=========================================================================================="
               echo""
               exit 1
            fi
        else
            if [[ -f $whl_cpu_develop ]];then
                $python_root -m pip installi -U $whl_cpu_develop
                if [[ $? == "0" ]];then
                   rm -rf $whl_cpu_develop
                   # TODO add install success check here
                   green "å®‰è£…æˆåŠŸï¼å°æç¤ºï¼šå¯ä»¥ä½¿ç”¨: ${python_root} æ¥å¯åŠ¨å®‰è£…äº†PaddlePaddleçš„Pythonè§£é‡Šå™¨"
                   break
                else
                   red "æœªèƒ½æ­£å¸¸å®‰è£…PaddlePaddleï¼Œè¯·å°è¯•æ›´æ¢æ‚¨è¾“å…¥çš„pythonè·¯å¾„ï¼Œæˆ–è€…ctrl + cé€€å‡ºåŽè¯·æ£€æŸ¥æ‚¨ä½¿ç”¨çš„pythonå¯¹åº”çš„pipæˆ–pipæºæ˜¯å¦å¯ç”¨"
                   echo""
                   echo "=========================================================================================="
                   echo""
                   exit 1
                fi
            else
                wget ${path}$whl_cpu_develop -O $whl_cpu_develop
                if [[ $? == "0" ]];then
                    $python_root -m pip install $whl_cpu_develop
                    if [[ $? == "0" ]];then
                       rm  $wheel_cpu_develop
                       green "å®‰è£…æˆåŠŸï¼Œå¯ä»¥ä½¿ç”¨: ${python_root} æ¥å¯åŠ¨å®‰è£…äº†PaddlePaddleçš„Pythonè§£é‡Šå™¨"
                       break
                    else
                       rm  $whl_cpu_release
                       red "æœªèƒ½æ­£å¸¸å®‰è£…PaddlePaddleï¼Œè¯·å°è¯•æ›´æ¢æ‚¨è¾“å…¥çš„pythonè·¯å¾„ï¼Œæˆ–è€…ctrl + cé€€å‡ºåŽè¯·æ£€æŸ¥æ‚¨ä½¿ç”¨çš„pythonå¯¹åº”çš„pipæˆ–pipæºæ˜¯å¦å¯ç”¨"
                       echo""
                       echo "=========================================================================================="
                       echo""
                       exit 1
                    fi
                else
                      rm  $whl_cpu_develop
                      red "æœªèƒ½æ­£å¸¸å®‰è£…PaddlePaddleï¼Œè¯·æ£€æŸ¥æ‚¨çš„ç½‘ç»œ æˆ–è€…ç¡®è®¤æ‚¨æ˜¯å¦å®‰è£…æœ‰ wgetï¼Œæˆ–è€…ctrl + cé€€å‡ºåŽåé¦ˆè‡³https://github.com/PaddlePaddle/Paddle/issues"
                      echo""
                      echo "=========================================================================================="
                      echo""
                      exit 1
                fi
            fi
        fi
  done
}

function main() {
  echo "*********************************"
  green "æ¬¢è¿Žä½¿ç”¨PaddlePaddleå¿«é€Ÿå®‰è£…è„šæœ¬"
  echo "*********************************"
  echo
  yellow "å¦‚æžœæ‚¨åœ¨å®‰è£…è¿‡ç¨‹ä¸­é‡åˆ°ä»»ä½•é—®é¢˜ï¼Œè¯·åœ¨https://github.com/PaddlePaddle/Paddle/issuesåé¦ˆï¼Œæˆ‘ä»¬çš„å·¥ä½œäººå‘˜å°†ä¼šå¸®æ‚¨ç­”ç–‘è§£æƒ‘"
  echo
  echo  "æœ¬å®‰è£…åŒ…å°†å¸®åŠ©æ‚¨åœ¨Linuxæˆ–Macç³»ç»Ÿä¸‹å®‰è£…PaddlePaddle,åŒ…æ‹¬"
  yellow "1ï¼‰å®‰è£…å‰çš„å‡†å¤‡"
  yellow "2ï¼‰å¼€å§‹å®‰è£…"
  echo
  read -n1 -p "è¯·æŒ‰å›žè½¦é”®è¿›è¡Œä¸‹ä¸€æ­¥..."
  echo
  echo
  green "*********************1. å®‰è£…å‰çš„å‡†å¤‡*****************************"
  echo
  echo "Step 1. æ­£åœ¨æ£€æµ‹æ‚¨çš„æ“ä½œç³»ç»Ÿä¿¡æ¯..."
  echo
  SYSTEM=`uname -s`
  if [[ "$SYSTEM" == "Darwin" ]];then
  	yellow "          æ‚¨çš„ç³»ç»Ÿä¸ºï¼šMAC OSX"
    echo
  	macos
  else
 	yellow "          æ‚¨çš„ç³»ç»Ÿä¸ºï¼šLinux"
  echo
	  OS=`cat /etc/issue|awk 'NR==1 {print $1}'`
	  if [[ $OS == "\S" ]] || [[ "$OS" == "CentOS" ]] || [[ $OS == "Ubuntu" ]];then
	    linux
	  else
	    red "æ‚¨çš„ç³»ç»Ÿä¸åœ¨æœ¬å®‰è£…åŒ…çš„æ”¯æŒèŒƒå›´ï¼Œå¦‚æ‚¨éœ€è¦åœ¨windowsçŽ¯å¢ƒä¸‹å®‰è£…PaddlePaddleï¼Œè¯·æ‚¨å‚è€ƒPaddlePaddleå®˜ç½‘çš„windowså®‰è£…æ–‡æ¡£"
	  fi
  fi
}
main