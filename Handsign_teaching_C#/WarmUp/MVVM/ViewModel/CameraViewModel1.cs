//using OpenCvSharp;
//using System.Windows.Media.Imaging;
//using System.Windows.Input;
//using WarmUp.Core; // Giả định đây là namespace chứa RelayCommand và InotifyChanged
//using OpenCvSharp.WpfExtensions;
//using System.Diagnostics;
//using System.Windows;
//using System.IO;
//using System.Threading;
//using System.Threading.Tasks;
//using System.Net.WebSockets;
//using System.Net.Sockets;
//using System.Net;
//using System.Text;
//using System.DirectoryServices;
//using System.Drawing;

//namespace WarmUp.MVVM.ViewModel
//{
//    internal class CameraViewModel : InotifyChanged
//    {
//        private VideoCapture capture;
//        private BitmapSource _cameraFrame1 = new BitmapImage(); // Frame gốc từ camera
//        private BitmapSource _cameraFrame2 = new BitmapImage();
//        private BitmapSource pre_img = new BitmapImage(); // Frame đã xử lý từ server
//        private Mat frame = new Mat();
//        private String text = "";
//        private Mat _lastestFrame = new Mat();
//        private BitmapSource img_test = new BitmapImage();
//        private bool _isCameraRunning = false;
//        static readonly object _frameLock = new object();
//        const string SERVER_IP = "127.0.0.1"; // địa chỉ Python server (local)
//        const int SERVER_PORT = 5001;         // cổng mặc định
//        private bool isRunning = true;
//        static List<string> frameNames = new List<string>();
//        private TcpClient _client;
//        private NetworkStream _networkStream;
//        protected string letter = "aa";
//        protected String src = "";
//        private int _Index = 0;
//        private BitmapSource Icon1 = new BitmapImage();
//        private readonly List<string> _questions = new List<string> { "aa", "aw", "oo", "sac", "hoi", "nang", "aw", "ow", "uw", "nga", "huyen" }; // Danh sách câu hỏi
//        private int _currentIndex = 0; // Chỉ số hiện tại trong danh sách
//        private List<BitmapImage> _logo;
//        public ICommand StartCameraCommand { get; }
//        public ICommand StopCameraCommand { get; } // Thêm lệnh dừng camera
//        private int cnt = 0;
//        public CameraViewModel()
//        {
//            var placeholder = LoadImage("D:\\hcmute\\apps\\C#\\WarmUp\\WarmUp\\Image\\Trang4\\icon_check.png");
//            Logos = Enumerable.Repeat(placeholder, 10).ToList();
//            StartCameraCommand = new RelayCommand(async () => await StartCamera());
//            StopCameraCommand = new RelayCommand(async () => await StopCamera()); // Thêm lệnh dừng
//        }

//        public BitmapSource CameraFrame
//        {
//            get => _cameraFrame1;
//            set
//            {
//                if (_cameraFrame1 != value)
//                {
//                    _cameraFrame1 = value;
//                    OnpropertyChanged();
//                }
//            }
//        }
//        public BitmapSource Processing_CameraFrame
//        {
//            get => _cameraFrame2;
//            set
//            {
//                if (_cameraFrame2 != value)
//                {
//                    _cameraFrame2 = value;
//                    OnpropertyChanged();
//                }
//            }
//        }

//        public Mat GetFrame
//        {
//            get => frame;
//            set { frame = value; OnpropertyChanged(); }
//        }
//        public String getText
//        {
//            get => text;
//            set
//            {
//                text = value; OnpropertyChanged();
//            }
//        }
//        public int showCnt
//        {
//            get => cnt;
//            set
//            {
//                if (cnt != value)
//                {
//                    cnt = value;
//                    OnpropertyChanged();
//                }
//            }
//        }
//        public BitmapSource GetImage
//        {
//            get => img_test;
//            set
//            {
//                img_test = value; OnpropertyChanged();
//            }
//        }
//        public List<BitmapImage> Logos
//        {
//            get => _logo;
//            set
//            {
//                if (_logo != value)
//                {
//                    _logo = value;
//                    OnpropertyChanged();
//                }
//            }
//        }

//        private BitmapImage LoadImage(string path)
//        {
//            if (string.IsNullOrEmpty(path))
//            {
//                throw new ArgumentException("Path cannot be empty.", nameof(path));
//            }
//            try
//            {
//                BitmapImage bitmap = new BitmapImage();
//                bitmap.BeginInit();
//                bitmap.UriSource = new Uri(path, UriKind.Absolute);
//                bitmap.EndInit();
//                return bitmap;
//            }
//            catch (Exception ex)
//            {
//                // Log the error or handle it appropriately
//                System.Diagnostics.Debug.WriteLine($"Failed to load image from {path}: {ex.Message}");
//                return null; // Or return a default image
//            }
//        }
//        private async Task StartCamera()
//        {
//            src = $"D:\\hcmute\\apps\\C#\\WarmUp\\WarmUp\\Image\\Trang 3\\{letter}.png";
//            Mat img = Cv2.ImRead(src);
//            pre_img = img.ToBitmapSource();
//            GetImage = pre_img;

//            if (_isCameraRunning) return;

//            Debug.WriteLine("Starting camera...");
//            capture = new VideoCapture(0);
//            if (!capture.IsOpened())
//            {
//                Debug.WriteLine("Cannot open camera");
//                return;
//            }

//            _lastestFrame = new Mat();
//            _isCameraRunning = true;
//            // Chạy các tác vụ song song
//            Task.Run(() => DisplayCamera());
//            _client = new TcpClient();
//            try
//            {
//                _client.Connect(SERVER_IP, SERVER_PORT);
//                Console.WriteLine($"Connected to Python server at {SERVER_IP}:{SERVER_PORT}");
//            }
//            catch (Exception ex)
//            {
//                Console.WriteLine("Lỗi kết nối đến server: " + ex.Message);
//                return;
//            }
//            _networkStream = _client.GetStream();
//            // Chạy luồng gửi/nhận dữ liệu
//            Task.Run(() => ProcessFrames(capture, _networkStream, this));
//        }
//        private void DisplayCamera()
//        {
//            while (_isCameraRunning)
//            {
//                if (capture == null || !capture.IsOpened()) break;
//                if (frame == null) frame = new Mat();  // khởi tạo nếu chưa có

//                capture.Read(frame);
//                if (frame.Empty()) continue;

//                var bitmap = frame.ToBitmapSource();
//                if (bitmap != null)
//                {
//                    bitmap.Freeze();
//                    Application.Current.Dispatcher.Invoke(() => CameraFrame = bitmap);
//                }
//                else
//                {
//                    StopCamera();
//                }

//                lock (_frameLock ?? new object()) // fallback nếu _frameLock null
//                {
//                    _lastestFrame?.Dispose(); // an toàn nếu null
//                    _lastestFrame = frame.Clone();
//                }

//                Thread.Sleep(33); // ~30 FPS
//            }
//        }

//        static void ProcessFrames(VideoCapture capture, NetworkStream networkStream, CameraViewModel viewModel)
//        {

//            while (viewModel.isRunning)
//            {
//                if (viewModel.getText != viewModel.letter)
//                {
//                    viewModel.src = $"D:\\hcmute\\apps\\C#\\WarmUp\\WarmUp\\Image\\Trang 3\\{viewModel.letter}.png";
//                    Mat img = Cv2.ImRead(viewModel.src);
//                    viewModel.pre_img = img.ToBitmapSource();
//                    viewModel.pre_img.Freeze();
//                    Application.Current.Dispatcher.Invoke(() => viewModel.GetImage = viewModel.pre_img);
//                }
//                Mat frame = new Mat();
//                lock (_frameLock)
//                {
//                    if (viewModel._lastestFrame != null)
//                        frame = viewModel._lastestFrame.Clone();
//                }

//                if (frame == null || frame.Empty())
//                {
//                    frame?.Dispose();
//                    Thread.Sleep(10);
//                    continue;
//                }

//                // Encode ảnh sang JPEG (sử dụng .ImEncode của OpenCvSharp)
//                byte[] jpegBytes = frame.ImEncode(".jpg");
//                frame.Dispose();

//                try
//                {
//                    // Gửi header (4-byte, big-endian) cho kích thước ảnh
//                    byte[] lengthBytes = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(jpegBytes.Length));
//                    networkStream.Write(lengthBytes, 0, lengthBytes.Length);

//                    // Gửi dữ liệu ảnh
//                    networkStream.Write(jpegBytes, 0, jpegBytes.Length);
//                    networkStream.Flush();

//                    // Nhận header phản hồi từ server (4 byte)
//                    byte[] respLengthBytes = ReadFromStream(networkStream, 4);
//                    if (respLengthBytes == null)
//                    {
//                        Console.WriteLine("Không nhận được header phản hồi.");
//                        continue;
//                    }
//                    int respLength = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(respLengthBytes, 0));
//                    if (respLength <= 0)
//                    {
//                        Console.WriteLine("Phản hồi có kích thước không hợp lệ.");
//                        continue;
//                    }
//                    // Nhận dữ liệu phản hồi đầy đủ
//                    byte[] respData = ReadFromStream(networkStream, respLength);
//                    if (respData == null)
//                    {
//                        Console.WriteLine("Không nhận được dữ liệu phản hồi đầy đủ.");
//                        continue;
//                    }
//                    string response = Encoding.UTF8.GetString(respData);
//                    //Console.WriteLine("Response from Python: " + response);
//                    viewModel.showCnt += 1;
//                    frameNames.Add(response);
//                    if (frameNames.Count % 30 == 0)
//                    {
//                        viewModel.showCnt = 0;
//                        viewModel.getText = frameNames[29]; // Sử dụng instance viewModel
//                        viewModel.UpdateLetterIfMatched(viewModel.getText);
//                        frameNames.Clear();
//                    }
//                }
//                catch (Exception ex)
//                {
//                    Console.WriteLine("Lỗi khi gửi/nhận dữ liệu: " + ex.Message);
//                    viewModel.isRunning = false;
//                    break;
//                }

//                Thread.Sleep(10);
//            }
//        }
//        static byte[] ReadFromStream(NetworkStream stream, int count)
//        {
//            byte[] buffer = new byte[count];
//            int offset = 0;
//            while (offset < count)
//            {
//                int readBytes = stream.Read(buffer, offset, count - offset);
//                if (readBytes == 0)
//                {
//                    Console.WriteLine("Kết nối đã bị đóng.");
//                    return null; // Kết nối đã đóng
//                }
//                offset += readBytes;
//            }
//            return buffer;
//        }

//        private void UpdateLetterIfMatched(string response)
//        {
//            if (_questions.Count == 0 || _currentIndex >= _questions.Count)
//            {
//                Debug.WriteLine("Đã hết câu hỏi hoặc danh sách rỗng.");
//                return;
//            }

//            if (response == _questions[_currentIndex])
//            {
//                _currentIndex++;

//                if (_currentIndex < _questions.Count)
//                {
//                    letter = _questions[_currentIndex];
//                    Debug.WriteLine($"Cập nhật letter thành: {letter}");
//                    if (_Index < Logos.Count)
//                    {
//                        // Update Logos on UI thread
//                        Application.Current.Dispatcher.Invoke(() =>
//                        {
//                            Logos[_Index] = LoadImage("D:\\hcmute\\apps\\C#\\WarmUp\\WarmUp\\Image\\Trang4\\check_true.png");
//                            Logos[_Index].Freeze();
//                            Logos = new List<BitmapImage>(Logos); // Notify UI of change
//                        });

//                        _Index++;
//                    }
//                }
//                else
//                {
//                    Debug.WriteLine("Đã hoàn thành tất cả câu hỏi.");
//                    letter = null;
//                }
//            }
//        }

//        private async Task StopCamera()
//        {
//            if (!_isCameraRunning) return;

//            Debug.WriteLine("Stopping camera...");
//            _isCameraRunning = false;
//            isRunning = false;

//            // Giải phóng tài nguyên
//            try
//            {
//                capture?.Release();
//                capture?.Dispose();
//                capture = null;

//                _networkStream?.Close();
//                _networkStream?.Dispose();
//                _networkStream = null;

//                _client?.Close();
//                _client?.Dispose();
//                _client = null;

//                lock (_frameLock)
//                {
//                    _lastestFrame?.Dispose();
//                    _lastestFrame = null;
//                }

//                frame?.Dispose();
//                frame = null;
//            }
//            catch (Exception ex)
//            {
//                Debug.WriteLine($"Lỗi khi dừng camera: {ex.Message}");
//            }

//            // Cập nhật UI (nếu cần)
//            Application.Current.Dispatcher.Invoke(() =>
//            {
//                CameraFrame = null; // Xóa frame hiển thị
//                Processing_CameraFrame = null;
//            });

//            Debug.WriteLine("Camera stopped.");
//        }

//    }
//}