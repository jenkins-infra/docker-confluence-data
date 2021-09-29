if [ -z "$UNITY_HOME" ]; then
  echo "Missing UNITY_HOME environment variable. Using default"
  UNITY_HOME=/Applications/Unity/Unity.app
fi

methods=`sed  -n 's/.*static void Perform\(.*\)Build ().*/\1/p' Assets/Editor/MyEditorScript.cs | sort | xargs echo`

if [ $# -ne 1 ]; then
  echo "ERROR: missing argument"
  echo "Usage: $0 method"
  echo "Methods available: $methods"
  exit -1
fi
method=$1
echo "UNITY_HOME $UNITY_HOME"
PROJECT_PATH=`pwd`
echo "Building $WORKSPACE"
#rm -rf target
mkdir -p target
$UNITY_HOME/Contents/MacOS/Unity -projectpath $PROJECT_PATH -quit -batchmode  -executeMethod "MyEditorScript.Perform${method}Build"
buildres=$?
if [ $buildres -ne 0 ]; then
  cat ~/Library/Logs/Unity/Editor.log
  ls -la ~/Library/Logs/Unity/Editor.log
else
  echo "Success building $method"
  ls -la target
fi
exit $buildres
