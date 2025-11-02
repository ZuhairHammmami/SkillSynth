// File: D:\SkillSynth\src\frontend\components\Header.tsx

// أولاً، نُعرّف "شكل" البيانات التي سيتلقاها هذا المكون.
// هذا يسمى "Props" (خصائص). نستخدم interface في TypeScript لهذا الغرض.
// هذا العقد يقول: "أي شخص يريد استخدام مكون Header، يجب أن يمرر لي خاصية اسمها userName ونوعها نص (string)".
interface HeaderProps {
  userName: string;
}

// هذه هي دالة المكون. لاحظ كيف نستخدم { userName }: HeaderProps
// هذه طريقة مختصرة لاستقبال الـ props وفكها مباشرةً للحصول على userName.
export default function Header({ userName }: HeaderProps) {
  return (
    // <header> هو عنصر HTML عادي، نستخدمه للدلالة على أن هذا هو رأس الصفحة.
    // className يحتوي على فئات Tailwind CSS للتصميم.
    // bg-gray-100: خلفية رمادية فاتحة.
    // border-b: إضافة خط سفلي.
    // p-4: إضافة حشوة (padding) من كل الجوانب.
    // flex, justify-between, items-center: لتوزيع العناصر بداخل الهيدر بشكل جميل (الشعار على اليسار واسم المستخدم على اليمين).
    <header className="border-b bg-gray-100 p-4">
      <div className="container mx-auto flex items-center justify-between">
        {/* الشعار */}
        <div className="text-xl font-bold">SkillSynth</div>
        
        {/* اسم المستخدم */}
        <div>مرحباً، {userName}</div>
      </div>
    </header>
  );
}