// المسار: E:/SkillSynth/refactor.js
// احفظ هذا الكود في ملف باسم `refactor.js` في جذر المشروع

const fs = require('fs');
const path = require('path');

// --- إعدادات ---
const FRONTEND_ROOT = path.join(__dirname, 'src', 'frontend');
const SRC_ROOT = path.join(FRONTEND_ROOT, 'src');

// --- دوال مساعدة ---
const log = (message) => console.log(`✅ ${message}`);
const logError = (message) => console.error(`❌ ${message}`);
const logInfo = (message) => console.log(`- ${message}`);

const createDir = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    log(`تم إنشاء المجلد: ${path.relative(__dirname, dirPath)}`);
  }
};

const moveFile = (oldPath, newPath) => {
  if (fs.existsSync(oldPath)) {
    // تأكد من وجود المجلد الهدف
    createDir(path.dirname(newPath));
    fs.renameSync(oldPath, newPath);
    log(`تم نقل الملف: ${path.relative(__dirname, oldPath)} -> ${path.relative(__dirname, newPath)}`);
  } else {
    logInfo(`الملف المصدر غير موجود، تم التخطي: ${path.relative(__dirname, oldPath)}`);
  }
};

// --- الخطة التنفيذية ---
async function runRefactor() {
  console.log('--- بدء عملية إعادة هيكلة الواجهة الأمامية (Frontend) ---');
  
  // --- المرحلة الأولى: إنشاء الهيكل الجديد ---
  logInfo('المرحلة 1: إنشاء هيكل المجلدات الجديد...');
  
  const featuresDir = path.join(SRC_ROOT, 'features');
  createDir(featuresDir);

  const featureFolders = ['auth', 'user', 'wizard', 'admin', 'paths'];
  featureFolders.forEach(feature => {
    createDir(path.join(featuresDir, feature, 'components'));
    createDir(path.join(featuresDir, feature, 'hooks'));
  });

  createDir(path.join(SRC_ROOT, 'hooks'));
  createDir(path.join(SRC_ROOT, 'store'));

  // --- المرحلة الثانية: نقل الملفات الموجودة ---
  logInfo('\nالمرحلة 2: نقل المكونات والصفحات الموجودة...');

  // نقل مكونات المصادقة
  moveFile(
    path.join(SRC_ROOT, 'app', '(auth)', 'login', 'page.tsx'), 
    path.join(featuresDir, 'auth', 'components', 'LoginForm.tsx')
  );
  moveFile(
    path.join(SRC_ROOT, 'app', '(auth)', 'register', 'page.tsx'),
    path.join(featuresDir, 'auth', 'components', 'RegisterForm.tsx')
  );
  moveFile(
    path.join(SRC_ROOT, 'app', '(auth)', 'forgot-password', 'page.tsx'),
    path.join(featuresDir, 'auth', 'components', 'ForgotPasswordForm.tsx')
  );
  moveFile(
    path.join(SRC_ROOT, 'app', '(auth)', 'reset-password', '[token]', 'page.tsx'),
    path.join(featuresDir, 'auth', 'components', 'ResetPasswordForm.tsx')
  );

  // نقل مكونات الملف الشخصي
  moveFile(
    path.join(SRC_ROOT, 'app', 'components', 'profile', 'UpdateProfileForm.tsx'),
    path.join(featuresDir, 'user', 'components', 'UpdateProfileForm.tsx')
  );
  moveFile(
    path.join(SRC_ROOT, 'app', 'components', 'profile', 'ChangePasswordForm.tsx'),
    path.join(featuresDir, 'user', 'components', 'ChangePasswordForm.tsx')
  );

  // نقل مكونات الـ Wizard
  const oldWizardDir = path.join(SRC_ROOT, 'app', 'components', 'wizard');
  if (fs.existsSync(oldWizardDir)) {
      const wizardFiles = fs.readdirSync(oldWizardDir);
      wizardFiles.forEach(file => {
          moveFile(
              path.join(oldWizardDir, file),
              path.join(featuresDir, 'wizard', 'components', file)
          );
      });
      // يمكن حذف المجلد القديم بعد نقل محتوياته
      // fs.rmdirSync(oldWizardDir); 
  }

  // نقل المكونات العامة المتبقية
  const generalComponents = ['AnimatedBackground.tsx', 'EmptyStateIllustration.tsx', 'Header.tsx', 'Logo.tsx', 'PathCard.tsx', 'StepItem.tsx'];
  generalComponents.forEach(comp => {
      moveFile(
          path.join(SRC_ROOT, 'app', 'components', comp),
          path.join(SRC_ROOT, 'components', comp) // نقلها إلى مجلد المكونات العام الجديد
      );
  });

  // --- المرحلة الثالثة: تنظيف المجلدات القديمة (اختياري) ---
  logInfo('\nالمرحلة 3: عملية النقل تمت. المجلدات القديمة مثل `app/components` قد تكون فارغة الآن.');
  logInfo('يمكنك حذفها يدويًا بعد التأكد من أن كل شيء تم نقله بنجاح.');

  console.log('\n--- 🎉 اكتملت عملية إعادة الهيكلة الآلية! ---');
  console.log('الخطوة التالية: يرجى مراجعة وتحديث مسارات `import` في الملفات التي تم نقلها.');
}

// تشغيل الخطة
runRefactor().catch(err => {
  logError('حدث خطأ فادح أثناء إعادة الهيكلة:');
  console.error(err);
});