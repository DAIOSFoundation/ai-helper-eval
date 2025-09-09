import React from 'react';
import menuItemsData from '../../data/sidebarMenuItems.json'; // JSON 파일 임포트

interface SidebarProps {
  currentView: string;
  onNavigate: (view: string) => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: string;
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate }) => {
  // JSON 파일에서 불러온 데이터를 사용합니다.
  const menuItems: MenuItem[] = menuItemsData;

  return (
    <div className="w-40 bg-white shadow-lg min-h-screen border-r border-gray-200 flex-shrink-0">
      <div className="p-2">
        <h2 className="text-xl font-bold text-indigo-800 mb-4 text-center px-2">
          AI Helper
        </h2>
        
        <nav className="space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center py-2 px-3 rounded-lg transition-colors text-left justify-start ${ // justify-start 클래스 추가
                currentView === item.id
                  ? 'btn-unified-primary'
                  : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              {/* 아이콘과 메뉴명 간격 10px로 조정 */}
              <span className="text-sm font-medium" style={{ marginLeft: '10px' }}>
                {item.label}
              </span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;